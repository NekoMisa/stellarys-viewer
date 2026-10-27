// Stellarys mirror mip regression checks. SPDX-License-Identifier: LGPL-2.1-only
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <GL/gl.h>
#include <array>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

template<typename T> T proc(const char* name)
{
    auto value = wglGetProcAddress(name);
    if (!value) throw std::runtime_error(std::string("Missing GL entry point: ")+name);
    return reinterpret_cast<T>(value);
}
using CreateShader=GLuint(APIENTRY*)(GLenum);
using ShaderSource=void(APIENTRY*)(GLuint,GLsizei,const char* const*,const GLint*);
using CompileShader=void(APIENTRY*)(GLuint);
using GetShaderiv=void(APIENTRY*)(GLuint,GLenum,GLint*);
using GetInfoLog=void(APIENTRY*)(GLuint,GLsizei,GLsizei*,char*);
using CreateProgram=GLuint(APIENTRY*)();
using AttachShader=void(APIENTRY*)(GLuint,GLuint);
using ProgramAction=void(APIENTRY*)(GLuint);
using GetProgramiv=void(APIENTRY*)(GLuint,GLenum,GLint*);
using GetUniformLocation=GLint(APIENTRY*)(GLuint,const char*);
using Uniform1i=void(APIENTRY*)(GLint,GLint);
using Uniform1f=void(APIENTRY*)(GLint,GLfloat);
using GenObjects=void(APIENTRY*)(GLsizei,GLuint*);
using BindObject=void(APIENTRY*)(GLenum,GLuint);
using BindVertexArray=void(APIENTRY*)(GLuint);
using TexImage3D=void(APIENTRY*)(GLenum,GLint,GLint,GLsizei,GLsizei,GLsizei,GLint,GLenum,GLenum,const void*);
using FramebufferTexture2D=void(APIENTRY*)(GLenum,GLenum,GLenum,GLuint,GLint);
using CheckFramebufferStatus=GLenum(APIENTRY*)(GLenum);

GLuint shader(GLenum type,const std::string& text)
{
    GLuint id=proc<CreateShader>("glCreateShader")(type);
    const char* p=text.c_str();proc<ShaderSource>("glShaderSource")(id,1,&p,nullptr);
    proc<CompileShader>("glCompileShader")(id);
    GLint good=0;proc<GetShaderiv>("glGetShaderiv")(id,0x8B81,&good);
    if (!good) { char log[8192]{};proc<GetInfoLog>("glGetShaderInfoLog")(id,sizeof(log),nullptr,log);throw std::runtime_error(log); }
    return id;
}
GLuint program(const char* file)
{
    std::ifstream in(file);if(!in)throw std::runtime_error("Cannot open shader");
    std::ostringstream source;source<<in.rdbuf();
    GLuint vert=shader(0x8B31,"#version 400 core\nvoid main(){vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);gl_Position=vec4(p*2.0-1.0,0,1);}\n");
    GLuint frag=shader(0x8B30,source.str());
    GLuint p=proc<CreateProgram>("glCreateProgram")();
    proc<AttachShader>("glAttachShader")(p,vert);proc<AttachShader>("glAttachShader")(p,frag);
    proc<ProgramAction>("glLinkProgram")(p);
    GLint good=0;proc<GetProgramiv>("glGetProgramiv")(p,0x8B82,&good);
    if(!good){char log[8192]{};proc<GetInfoLog>("glGetProgramInfoLog")(p,sizeof(log),nullptr,log);throw std::runtime_error(log);}
    return p;
}

int main(int argc,char** argv)
{
    if(argc!=2 && argc!=3)return 2;
    const bool compare = argc==3;
    HWND window=CreateWindowExW(0,L"STATIC",L"Disposable mirror mip check",WS_POPUP,0,0,16,16,nullptr,nullptr,GetModuleHandleW(nullptr),nullptr);
    HDC dc=GetDC(window);PIXELFORMATDESCRIPTOR pixel{};
    pixel.nSize=sizeof(pixel);pixel.nVersion=1;pixel.dwFlags=PFD_DRAW_TO_WINDOW|PFD_SUPPORT_OPENGL|PFD_DOUBLEBUFFER;
    pixel.iPixelType=PFD_TYPE_RGBA;pixel.cColorBits=24;
    int format=ChoosePixelFormat(dc,&pixel);
    if(!format||!SetPixelFormat(dc,format,&pixel))return 3;
    HGLRC context=wglCreateContext(dc);if(!context||!wglMakeCurrent(dc,context))return 4;
    int result=0;
    try
    {
        std::cout<<"GPU: "<<glGetString(GL_RENDERER)<<"; OpenGL: "<<glGetString(GL_VERSION)<<'\n';
        GLuint programs[2]={program(argv[1]),compare ? program(argv[2]) : 0};
        GLuint vao=0;proc<GenObjects>("glGenVertexArrays")(1,&vao);proc<BindVertexArray>("glBindVertexArray")(vao);
        GLuint output=0;glGenTextures(1,&output);glBindTexture(GL_TEXTURE_2D,output);
        glTexImage2D(GL_TEXTURE_2D,0,0x8814,1,1,0,GL_RGBA,GL_FLOAT,nullptr); // RGBA32F
        GLuint fbo=0;proc<GenObjects>("glGenFramebuffers")(1,&fbo);proc<BindObject>("glBindFramebuffer")(0x8D40,fbo);
        proc<FramebufferTexture2D>("glFramebufferTexture2D")(0x8D40,0x8CE0,GL_TEXTURE_2D,output,0);
        if(proc<CheckFramebufferStatus>("glCheckFramebufferStatus")(0x8D40)!=0x8CD5)throw std::runtime_error("Incomplete FBO");
        glViewport(0,0,1,1);glDisable(GL_DITHER);glDisable(GL_BLEND);
        GLuint cube=0;glGenTextures(1,&cube);glBindTexture(0x9009,cube); // CUBE_MAP_ARRAY
        glTexParameteri(0x9009,GL_TEXTURE_MIN_FILTER,0x2703); // LINEAR_MIPMAP_LINEAR
        glTexParameteri(0x9009,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
        glTexParameteri(0x9009,0x813D,4); // MAX_LEVEL
        for(GLenum axis:std::array<GLenum,3>{GL_TEXTURE_WRAP_S,GL_TEXTURE_WRAP_T,0x8072})glTexParameteri(0x9009,axis,0x812F);
        int checks=0,originalCorrupt=0;
        for(int count:{6,7,8,9,10,11,12})for(bool poisonNan:{false,true})
        {
            const int generated=count/4;
            for(int mip=0;mip<=4;++mip)
            {
                int size=16>>mip;std::vector<float> data(size*size*6*4);
                const std::array<float,4> color=mip<generated ? std::array<float,4>{0.2f,0.4f,0.8f,1.f} :
                    poisonNan ? std::array<float,4>{std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::quiet_NaN(),1.f} :
                    std::array<float,4>{8.f,0.f,4.f,1.f};
                for(size_t i=0;i<data.size();++i)data[i]=color[i%4];
                proc<TexImage3D>("glTexImage3D")(0x9009,mip,0x8814,size,size,6,0,GL_RGBA,GL_FLOAT,data.data());
            }
            for(int step=0;step<=100;++step)
            {
                float gloss=step/100.f;
                const float weight=std::max(0.f,std::min(1.f,(gloss-0.75f)*4.f));
                const std::array<float,3> initial{0.1f,0.2f,0.3f},reflected{0.2f,0.4f,0.8f};
                for(int variant=0;variant<(compare ? 2 : 1);++variant)
                {
                    GLuint p=programs[variant];proc<ProgramAction>("glUseProgram")(p);
                    proc<Uniform1i>("glUniform1i")(proc<GetUniformLocation>("glGetUniformLocation")(p,"heroProbes"),0);
                    proc<Uniform1i>("glUniform1i")(proc<GetUniformLocation>("glGetUniformLocation")(p,"heroMipCount"),count);
                    proc<Uniform1f>("glUniform1f")(proc<GetUniformLocation>("glGetUniformLocation")(p,"testGlossiness"),gloss);
                    glDrawArrays(GL_TRIANGLES,0,3);
                    std::array<float,4> value{};glReadPixels(0,0,1,1,GL_RGBA,GL_FLOAT,value.data());
                    bool good=true;
                    for(int i=0;i<3;++i)
                        good=good&&std::isfinite(value[i])&&std::abs(value[i]-(initial[i]*(1-weight)+reflected[i]*weight))<0.002f;
                    if(compare && variant==0 && !good)++originalCorrupt;
                    if((!compare || variant==1) && !good)throw std::runtime_error("Guarded shader sampled poisoned/unwritten mip levels");
                    ++checks;
                }
            }
        }
        if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("OpenGL error during draw checks");
        if(compare && originalCorrupt==0)throw std::runtime_error("Test failed to demonstrate the original invalid-mip sampling");
        std::cout<<checks<<" total GPU draws: "<<checks/(compare ? 2 : 1)<<" guarded checks passed; reference mismatched expected color in "<<originalCorrupt<<" comparison draws with deliberately poisoned unused mip levels.\n";
        std::cout<<"Synthetic regression test; in-world results must be recorded separately.\n";
    }
    catch(const std::exception& e){std::cerr<<e.what()<<'\n';result=1;}
    wglMakeCurrent(nullptr,nullptr);wglDeleteContext(context);ReleaseDC(window,dc);DestroyWindow(window);
    return result;
}
