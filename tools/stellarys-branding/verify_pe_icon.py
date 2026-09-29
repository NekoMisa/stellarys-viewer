"""Read PE resources without loading/running the executable; verify icon data."""
from pathlib import Path
import hashlib, struct, json, sys

def digest(data): return hashlib.sha256(data).hexdigest()

def ico_frames(path):
    data=Path(path).read_bytes()
    reserved,kind,count=struct.unpack_from('<HHH',data)
    assert reserved==0 and kind==1
    frames={}
    for i in range(count):
        width,height,colors,pad,planes,depth,size,offset=struct.unpack_from('<BBBBHHII',data,6+16*i)
        frames[(width or 256,height or 256)]=digest(data[offset:offset+size])
    return frames

def resources(path):
    data=Path(path).read_bytes()
    pe=struct.unpack_from('<I',data,0x3c)[0]
    assert data[pe:pe+4]==b'PE\0\0'
    count=struct.unpack_from('<H',data,pe+6)[0]
    optsize=struct.unpack_from('<H',data,pe+20)[0]
    opt=pe+24;magic=struct.unpack_from('<H',data,opt)[0]
    assert magic in (0x10b,0x20b)
    dirs=opt+(112 if magic==0x20b else 96)
    sections=[]
    for i in range(count):
        s=opt+optsize+i*40
        virtual_size,rva,raw_size,raw=struct.unpack_from('<IIII',data,s+8)
        sections.append((rva,max(virtual_size,raw_size),raw))
    def offset(rva):
        for start,size,raw in sections:
            if start<=rva<start+size:return raw+rva-start
        raise ValueError('Resource RVA outside sections')
    root_rva=struct.unpack_from('<I',data,dirs+2*8)[0]
    root=offset(root_rva);found={}
    def walk(relative,keys=()):
        p=root+relative
        named,ids=struct.unpack_from('<HH',data,p+12)
        for i in range(named+ids):
            name,child=struct.unpack_from('<II',data,p+16+8*i)
            if name & 0x80000000:
                n=root+(name & 0x7fffffff)
                length=struct.unpack_from('<H',data,n)[0]
                key=data[n+2:n+2+length*2].decode('utf-16-le')
            else:key=name
            if child & 0x80000000:walk(child & 0x7fffffff,keys+(key,))
            else:
                rva,size=struct.unpack_from('<II',data,root+child)
                start=offset(rva);found[keys+(key,)]=data[start:start+size]
    walk(0)
    cert=struct.unpack_from('<II',data,dirs+4*8)
    return found,cert

def verify(executable,icon,required_groups=()):
    expected=ico_frames(icon);res,cert=resources(executable)
    assert cert==(0,0),'Unexpected executable signature'
    images={keys[1]:blob for keys,blob in res.items() if keys[0]==3}
    matches=[]
    for keys,group in res.items():
        if keys[0]!=14:continue
        frames={}
        reserved,kind,count=struct.unpack_from('<HHH',group)
        assert reserved==0 and kind==1
        for i in range(count):
            width,height,colors,pad,planes,depth,size,image_id=struct.unpack_from('<BBBBHHIH',group,6+i*14)
            image=images[image_id]
            assert len(image)==size
            frames[(width or 256,height or 256)]=digest(image)
        if frames==expected:matches.append(keys[1])
    assert matches,'No embedded icon group matches approved icon frames'
    assert set(required_groups)<=set(matches),'Required viewer icon groups do not match'
    return {'executable':Path(executable).name,'matching_groups':matches,
        'frame_sizes':[list(x) for x in sorted(expected)],'unsigned_certificate_table':True}

if __name__=='__main__':
    print(json.dumps(verify(sys.argv[1],sys.argv[2]),indent=2))
