import sys
import json
import os
import sqlite3
import re
import subprocess
import shutil
import hashlib
import binascii

import numpy as np
"""
[hash]/
    raw/
        *stuff*
        
    obj/
        [hash].obj   (with [hash].html)
        [hash].mtl
        *images*
        
    [hash].json
        "type": which converter to apply
        "misc": misc data from original sources
        *etc*
        
"""

META = None

def digimation_get_base_data(dbfile, outfile):
    conn = sqlite3.connect(dbfile)  
    cursor = conn.cursor() 

    cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
    schema = cursor.fetchall()
    data = {}
    
    
    for t in schema:
        tname = t[1]    
        cursor.execute('SELECT * from %s' % tname)
        d = cursor.fetchall()
        fields = [x[0] for x in cursor.description]
        d1 = [dict(zip(fields, r)) for r in d]
        data[tname] = d1
    
    base_data = data['Product_Models']
    for b in base_data:
        dat = [x for x in data['Products'] if x['ProductID_int'] == b['ProductID_int']][0]
        b.update(dat)
        
    for b in base_data:
        dat = [x for x in data['ProductCategoryProducts'] if x['ProductID_int'] == b['ProductID_int']][0]
        cat = [x for x in data['ProductCategories'] if x['ProductCategoryID_int'] == dat['ProductCategoryID_int']][0]
        b.update(cat)
        
    for b in base_data:
        b['ProductEncryptionKey2_binary'] = binascii.b2a_base64(b['ProductEncryptionKey2_binary'][:])
        if b['Product_ModelGroups_vchar']:
            b['Product_ModelGroups_vchar'] = b['Product_ModelGroups_vchar'].split('\n')
        b.pop('rowversion', None)
        
    dictv = {}
    for b in base_data:
        dictv[b['ProductCode_vchar']] = b
    with open(outfile, 'w') as _f:
        json.dump(dictv, _f)

"""
exploring the data
L = os.listdir('.')     
L1 = [(l, os.listdir(l)) for l in L if os.path.isdir(l)]
numobj = map(lambda x: len([y for y in x[1] if y.endswith('.obj')]), L1)
bad = [(m[0], n) for m, n in zip(L1, numobj) if n > 1 ]
nomtl = [l for l, k in L1 if not any([y.endswith('.mtl') for y in k])]

nummtl = map(lambda x: len([y for y in x[1] if y.endswith('.mtl')]), L1)
badmtl = [(m[0], n) for m, n in zip(L1, nummtl) if n > 1 ]

meta = json.load(open('Archive.json'))
prods = [y['ProductCode_vchar'] for y in meta]
nometa = [m[0] for m in L1 if m[0] not in prods]  #nothing
"""


class MTLError(Exception):
    pass

class NoMTLError(Exception):
    pass
    
class MissingTextureError(Exception):
    pass
    

img_exts = (".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".png")
# .mtl image fields
mtl_img_fields = ("map_ka", "map_kd", "map_ks", "map_ks", "map_d", "disp",
                  "decal", "map_bump", "bump", "map_refl", "refl")  


def parse_mtl_imgs(mtl_pth, f_edit=False, imgdirname="tex"):
    """ Search through the mtl_pth for all image file names and return
    as a list.  f_edit will substitute fixed img names into the .mtl
    file. 
    TODO:  parse options in bump declaration (e.g. -bm 0.00) without interfering with image names
           --related, handle image filenames with spaces better
    """
    # RE pattern
    pat_fields = "(?:" + "|".join(mtl_img_fields) + ") "
    pat_img_exts = "(.+(?:\\" + "|\\".join(img_exts) + "))"
    patstr = "[\s]*" + pat_fields + "((?:.*[/\\\\])?" + pat_img_exts + ")"
    rx = re.compile(patstr, re.IGNORECASE)
    ## Get the image file names from the .mtl file
    # Open .mtl
    with open(mtl_pth, "r") as fid:
        filestr = fid.read()
    if f_edit:
        def repl(m):
            # Get the old file name
            name = m.group(2).lower()
            # Store name
            mtlnames.append(name)
            # Pull out the path and image name
            newname = os.path.join(imgdirname, name)
            # First and last points in match
            i = m.start(1) - m.start()
            j = m.end(1) - m.start()
            match = m.group()
            # Make a substitute for the match
            newmatch = match[:i] + newname + match[j:]
            return newmatch
        # Initialize storage for the image file names from inside the
        # .mtl, which will be appended to by the repl function
        mtlnames = []
        # Search for matches and substitute in fixed path
        newfilestr = rx.subn(repl, filestr)[0]
        # Edit and save new .mtl
        with open(mtl_pth, "w") as fid:
            fid.write(newfilestr)
    else:
        # The .mtl's image filenames
        mtlnames = [m.group(2).lower() for m in rx.finditer(filestr)]
    return mtlnames
    

def parse_dir_imgs(root_pth):
    """ Search through pth and all sub-directories for image files and
    return a list of their names."""
    def visit(imgpths, pth, names):
        # Appends detected image filenames to a list.
        imgpths.extend([os.path.join(pth, name) for name in names
                        if os.path.splitext(name)[1].lower() in img_exts])
    # Walk down directory tree and get the image file paths
    imgpaths = []
    for dp, foo, names in os.walk(root_pth):
        visit(imgpaths, dp, names)
    # Make lowercased list of imagefilenames
    imgnames = [os.path.split(pth)[1].lower() for pth in imgpaths]
    return imgnames, imgpaths


def fix_tex_names(mtl_pth, imgdirname="tex", f_verify=True):            
    """ Make all .mtl image file names lowercase and relative paths,
    so they are compatible with linux and are portable.  Also change
    the actual image file names."""
    # Make the path absolute
    if not os.path.isabs(mtl_pth):
        mtl_pth = os.path.join(os.getcwd(), mtl_pth)
    # Directory path that the file is in
    dir_pth = os.path.split(mtl_pth)[0]
    # Directory for the images to go
    img_pth = os.path.join(dir_pth, imgdirname)

    # Parse the .mtl file for the image names
    mtlnames = parse_mtl_imgs(mtl_pth, f_edit=True, imgdirname=imgdirname)
    # Get image file names
    imgnames, imgpaths0 = parse_dir_imgs(dir_pth)
    # Check that all .mtl img names are present
    if f_verify and not set(mtlnames) <= set(imgnames):
        missingnames = ", ".join(set(imgnames) - set(mtlnames))
        raise MissingTextureError("Cannot find .mtl-defined images. "
                         "mtl: %s. imgs: %s" % (mtl_pth, missingnames))

    # Make the directory if need be, and error if it is a file already
    if os.path.isfile(img_pth):
        raise IOError("File exists: '%s'")
    elif not os.path.isdir(img_pth):
        # Make image directory, if necessary
        os.makedirs(img_pth)
    
    # Move the image files to the new img_pth location
    for imgpath0, imgname in zip(imgpaths0, imgnames):
        imgpath = os.path.join(img_pth, imgname)
        shutil.move(imgpath0, imgpath)


def get_hash(dirn):
    command = "find '%s' -type f -print0 | sort -z | xargs -0 sha1sum" % dirn
    proc = subprocess.Popen(command,stdout=subprocess.PIPE,shell=True)
    (out, err) = proc.communicate()
    if err is not None:
        print("Error getting hash for %s" % dirn)
    else:
        r = out.strip().split('\n')
        strs = []
        for _r in r:
            sha1 = _r.split(' ')[0]
            fn = os.path.relpath(' '.join(_r.split(' ')[1:]).strip(), start=dirn)
            strs.append(sha1 + '  ' + fn)
    strv = ''.join(strs)
    return hashlib.sha1(strv).hexdigest()
            

def get_mtl_ref(opath):
    ostr = open(opath).read()
    pat = re.compile('mtllib ([\S]+)')
    res = pat.search(ostr)
    if not res:
        raise MTLError('No mtllib declaration found in %s' % opath)
    ref = res.groups()[0]
    if not ref.endswith('.mtl'):
        raise MTLError('mtllib path in %s is weird: %s' % (opath, ref))
    return ref


def set_obj_name(name, opath, mpath):
    dirn, onm = os.path.split(opath)
    dirn, mnm = os.path.split(mpath)
    onm = os.path.splitext(onm)[0]
    mnm = os.path.splitext(mnm)[0]
    if onm != name:
        newopath = os.path.join(dirn, name + '.obj')
        shutil.move(opath, newopath)
        opath = newopath
    if mnm != name:
        newmtlpath = os.path.join(dirn, name + '.mtl')
        shutil.move(mpath, newmtlpath)
        mtlpath = newmtlpath
        
    mtln = get_mtl_ref(opath)
    ostr = open(opath).read()
    if mtln != name + '.mtl':
        ostr = ostr.replace(mtln, name + '.mtl')
        with open(opath, 'w') as _f:
            _f.write(ostr)
        
  
def correct_digimation(dirn, outdir, metapath):
    """
        check if there's an mtl file
            if not, raise NoMTLError
            
        for all objs in dir:
            look at referenced mtl
                if present, use it 
                else assert there's only mtl, otherwise raise noMTLError
            mk tempdir containing the obj, the mtl, and all non-obj/mtl files
            get hash
            fix stuff:
                name mtl same as obj
                make the name of the mtl in the obj correct
            mk new obj dir with correct stuff in it, with proper names and JSON
                use JSON from original enclosing dirname
    """
    global META
    if META is None:
        META = json.loads(open(metapath).read())
    dirn = os.path.abspath(dirn)
    oname = os.path.split(dirn)[1]
    metarec = META[oname]

    outdir = os.path.abspath(outdir)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    
    lst = [os.path.join(dirn, _l) for _l in os.listdir(dirn)]
    if not any([x.endswith('.mtl') for x in lst]):
        raise NoMTLError('No .mtl file found in %s' % dirn)
        
    objs = filter(lambda x: x.endswith('.obj'), lst)
    mtls = filter(lambda x: x.endswith('.mtl'), lst)
    
    for objf in objs:
        objf_loc = os.path.split(objf)[1]
        mtlf = get_mtl_ref(objf)
        if mtlf not in mtls:
            assert len(mtls) == 1, mtls
            mtlf = mtls[0]
            print('Mtl missing for %s, using %s' % (objf, mtlf))
        mtlf_loc = os.path.split(mtlf)[1]
        
        tmpname = str(np.random.randint(1e8))
        tmpdir = os.path.join(outdir, tmpname)
        os.makedirs(tmpdir)
        hash_files = [objf, mtlf] 
        for f in hash_files:
            relname = os.path.relpath(f, start=dirn)
            newf = os.path.join(tmpdir, relname)
            shutil.copy(f, newf)
        hash = get_hash(tmpdir)
        shutil.rmtree(tmpdir)
        
        newdir = os.path.join(outdir, hash)
        rawdir = os.path.join(newdir, 'raw')
        objdir = os.path.join(newdir, 'obj')
        os.makedirs(newdir)
        os.makedirs(rawdir)

        relevant_files = filter(lambda x: not x.endswith(('.obj', '.mtl')), lst)
        relevant_files += [objf, mtlf]
        for f in relevant_files:
            relname = os.path.relpath(f, start=dirn)
            newf = os.path.join(rawdir, relname)
            _dir = os.path.split(newf)[0]
            if not os.path.isdir(_dir):
                os.makedirs(_dir)
            shutil.copy(f, newf)
        
        shutil.copytree(rawdir, objdir)
        
        mtl_path = os.path.join(objdir, mtlf_loc)   
        fix_tex_names(mtl_path, imgdirname="tex", f_verify=True)
                        
        obj_path = os.path.join(objdir, objf_loc)
        set_obj_name(hash, obj_path, mtl_path)

        metapath = os.path.join(newdir, hash + '.json')
        with open(metapath, 'w') as _f:
            metarec = {'type': 'digimation',
                       'original_data': metarec}
            json.dump(metarec, _f)


if __name__ == '__main__':
    argv = sys.argv
    outdir = argv[1]
    dirn = argv[2]
    metapath = argv[3]
    correct_digimation(dirn, outdir, metapath)
