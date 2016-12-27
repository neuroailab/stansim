#pragma once

#include "GlobalAppState.h"
#include "Lighting.h"

class RenderObject {
public:
	RenderObject(GraphicsDevice& g, const TriMeshf& triMesh, const Materialf& material, const mat4f& modelToWorld) {
		m_triMesh.init(g, triMesh);

		m_material = material;
		if (m_material.m_TextureFilename_Kd != "") {
			std::string texFile = m_material.m_TextureFilename_Kd;
			//that's a hack because I don't know how to load exrs (manually converted with imagemagick)
			if (util::getFileExtension(texFile) == "exr") {
				texFile = util::replace(texFile, ".exr", ".png");
			}

			if (util::fileExists(texFile)) {
				try {
				std::cout << "loading " << texFile << "... ";
					ColorImageR8G8B8A8 tex;
					FreeImageWrapper::loadImage(texFile, tex);
					//tex.setPixels(vec4uc(255, 0, 0, 255));	//debug
					m_texture.init(g, tex);
					std::cout << "done!" << std::endl;
				}
				catch (const std::exception& e) {
					std::cout << texFile << " : " << e.what() << std::endl;
				}
			}
			else {
				std::cout << "can't file tex file " << texFile << std::endl;
			}
		}

		m_modelToWorld = modelToWorld;
		for (const auto& v : triMesh.getVertices())  {
			m_boundingBoxWorld.include(m_modelToWorld * v.position);
		}
	}

	~RenderObject() {

	}

	const mat4f& getModelToWorld() const {
		return m_modelToWorld;
	}

	const D3D11TriMesh& getD3D11TriMesh() const {
		return m_triMesh;
	}

	const D3D11Texture2D<vec4uc> &getD3D11Texture2D() const {
		return m_texture;
	}

	const BoundingBox3f& getBoundingBoxWorld() const {
		return m_boundingBoxWorld;
	}

	const Materialf& getMaterial() const {
		return m_material;
	}


	const bool isTextured() const {
		return m_texture.isInit();
	}

private:
	mat4f					m_modelToWorld;
	D3D11TriMesh			m_triMesh;
	D3D11Texture2D<vec4uc>	m_texture;
	BoundingBox3f			m_boundingBoxWorld;
	
	Materialf				m_material;
};



class Scene
{
public:
	Scene() {}

	~Scene() {}

	void init(GraphicsDevice& g, const std::vector<std::string>& meshFilenames);



	void render(const Cameraf& camera); 

	const BoundingBox3f& getBoundingBox() const {
		return m_boundingBox;
	}

	void randomizeLighting() {
		m_lighting.randomize();
	}

	const Lighting& getLighting() const {
		return m_lighting;
	}

	void setLighting(const Lighting& l) {
		m_lighting = l;
	}

private:

	void addObject(const TriMeshf& triMesh, const Materialf& material, const mat4f& modelToWorld = mat4f::identity()) {
		m_objects.emplace_back(RenderObject(*m_graphics, triMesh, material, modelToWorld));
		m_boundingBox.include(m_objects.back().getBoundingBoxWorld());
	}

	struct ConstantBufferCamera {
		mat4f worldViewProj;
		mat4f world;
		vec4f eye;
	};

	struct ConstantBufferMaterial {
		vec4f ambient;
		vec4f diffuse;
		vec4f specular;
		float shiny;
		vec3f dummy;
	};


	GraphicsDevice* m_graphics;

	D3D11ShaderManager m_shaders;

	std::vector<RenderObject> m_objects;
	BoundingBox3f m_boundingBox;


	D3D11ConstantBuffer<ConstantBufferCamera>	m_cbCamera;
	D3D11ConstantBuffer<ConstantBufferMaterial> m_cbMaterial;
	Lighting m_lighting;
};

