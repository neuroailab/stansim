
#include "stdafx.h"
#include "Scene.h"

void Scene::init(GraphicsDevice& g, const std::vector<std::string>& meshFilenames)
{

	m_graphics = &g;

	m_cbCamera.init(g);
	m_cbMaterial.init(g);
	m_lighting.loadFromGlobaAppState(g);

	//TODO factor our the shader loading; ideally every object has a shader
	m_shaders.init(g);
	m_shaders.registerShader("shaders/phong.hlsl", "phong", "vertexShaderMain", "vs_4_0", "pixelShaderMain", "ps_4_0");
	m_shaders.registerShader("shaders/phong.hlsl", "phong_textured", "vertexShaderMain", "vs_4_0", "pixelShaderMain_textured", "ps_4_0");

	for (const std::string& meshFilename : meshFilenames) {
		MeshDataf meshDataAll = MeshIOf::loadFromFile(meshFilename);

		std::vector< std::pair <MeshDataf, Materialf > > meshDataByMaterial = meshDataAll.splitByMaterial();

		for (auto& m : meshDataByMaterial) {

			MeshDataf& meshData = m.first;
			Materialf& material = m.second;

			MLIB_ASSERT(meshData.isConsistent());
			if (!meshData.isTriMesh()) {
				std::cout << "Warning mesh " << meshFilename << " contains non-tri faces (auto-converting)" << std::endl;
				meshData.makeTriMesh();
			}


			MLIB_ASSERT(meshData.isConsistent());
			if (meshData.m_Colors.size() == 0) meshData.m_Colors.resize(meshData.m_Vertices.size(), vec4f(1.0f, 1.0f, 1.0f, 1.0f));	//set default color if none present
			TriMeshf triMesh(meshData);
			if (!triMesh.hasNormals())	triMesh.computeNormals();

			material.m_ambient = vec4f(0.1f);

			std::string path = util::directoryFromPath(meshFilename);
			if (material.m_TextureFilename_Kd != "") material.m_TextureFilename_Kd = path + material.m_TextureFilename_Kd;
			addObject(triMesh, material);
		}

	}
}

void Scene::render(const Cameraf& camera)
{
	m_lighting.updateAndBind(2);

	for (const RenderObject& o : m_objects) {
		ConstantBufferCamera cbCamera;
		cbCamera.worldViewProj = camera.getPerspective() * camera.getCamera() * o.getModelToWorld();
		cbCamera.world = o.getModelToWorld();
		cbCamera.eye = vec4f(camera.getEye());
		m_cbCamera.updateAndBind(cbCamera, 0);

		const Materialf material = o.getMaterial();

		ConstantBufferMaterial cbMaterial;
		cbMaterial.ambient = material.m_ambient;
		cbMaterial.diffuse = material.m_diffuse;
		cbMaterial.specular = material.m_specular;
		cbMaterial.shiny = material.m_shiny;
		m_cbMaterial.updateAndBind(cbMaterial, 1);

		if (o.isTextured()) {
			o.getD3D11Texture2D().bind(0);
			m_shaders.bindShaders("phong_textured");
		}
		else {
			m_shaders.bindShaders("phong");
		}
		o.getD3D11TriMesh().render();

		if (o.isTextured()) {
			o.getD3D11Texture2D().unbind(0);
		}
	}
}
