#!/usr/bin/env python3
"""Use the supplied single flat 2026 mount to update the COMPLETE RV01 assembly.

Source: the one-part obj_42+bed+mount.3mf supplied by the maintainer.
Target: the original complete A1+bed+dragchain+RV01.3mf assembly.
Only the old bed-mount mesh is replaced. Python 3.10+, standard library only.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,zipfile
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
NS={'c':CORE}
ET.register_namespace('p',PROD)
IDENTITY='1 0 0 0 1 0 0 0 1 0 0 0'

def xml_bytes(root,relationships=False):
    ET.register_namespace('',REL if relationships else CORE)
    value=ET.tostring(root,encoding='UTF-8',xml_declaration=True)
    ET.register_namespace('',CORE)
    return value

def matrix(value):
    m=list(map(float,value.split()))
    if len(m)!=12:raise ValueError('Expected a 3MF affine matrix')
    for i in range(3):
        for j in range(3):
            dot=sum(m[i*3+k]*m[j*3+k] for k in range(3))
            if abs(dot-(1 if i==j else 0))>1e-7:raise ValueError('Only rigid transformations are supported; no scaling is permitted')
    return m

def apply(point,value):
    m=matrix(value);x,y,z=point
    return [x*m[0]+y*m[3]+z*m[6]+m[9],x*m[1]+y*m[4]+z*m[7]+m[10],x*m[2]+y*m[5]+z*m[8]+m[11]]

def inverse(point,value):
    m=matrix(value);q=[point[i]-m[i+9] for i in range(3)]
    return [sum(q[k]*m[3*i+k] for k in range(3)) for i in range(3)]

def bounds(vertices):
    return ([min(v[i] for v in vertices) for i in range(3)],[max(v[i] for v in vertices) for i in range(3)])

def part(archive,root,build):
    parent=root.find(f"c:resources/c:object[@id='{build.get('objectid')}']",NS)
    components=parent.findall('c:components/c:component',NS)
    if len(components)!=1:raise ValueError('Expected one mesh component for the mount')
    component=components[0]
    path=component.get(f'{{{PROD}}}path').lstrip('/')
    model=ET.fromstring(archive.read(path))
    obj=model.find(f"c:resources/c:object[@id='{component.get('objectid')}']",NS)
    mesh=obj.find('c:mesh',NS)
    vertices=[[float(e.get(a)) for a in 'xyz'] for e in mesh.findall('c:vertices/c:vertex',NS)]
    world=[apply(apply(v,component.get('transform',IDENTITY)),build.get('transform',IDENTITY)) for v in vertices]
    return component,path,model,obj,mesh,world

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path,help='The supplied single flat 2026 mount (obj_42+bed+mount.3mf)')
    parser.add_argument('target',type=Path,help='The ORIGINAL complete RV01 assembly with the old mount')
    parser.add_argument('--output',type=Path,required=True,help='New complete assembly 3MF')
    args=parser.parse_args()
    if args.output.exists():raise SystemExit('Choose a new output file.')
    with zipfile.ZipFile(args.source) as source,zipfile.ZipFile(args.target) as target:
        source_root=ET.fromstring(source.read('3D/3dmodel.model'))
        target_root=ET.fromstring(target.read('3D/3dmodel.model'))
        source_builds=source_root.findall('c:build/c:item',NS)
        target_builds=target_root.findall('c:build/c:item',NS)
        if len(source_builds)!=1 or len(target_builds)<2:
            raise SystemExit('Wrong direction: source must be the SINGLE flat 2026 mount, target must be the COMPLETE RV01 assembly.')
        source_component,source_path,source_model,source_obj,source_mesh,source_world=part(source,source_root,source_builds[0])
        source_faces=len(source_mesh.findall('c:triangles/c:triangle',NS))
        if source_faces!=17610:raise SystemExit('This recipe expects the supplied flat 2026 mesh (17,610 triangles).')
        settings=ET.fromstring(target.read('Metadata/model_settings.config'))
        candidates=[o for o in settings.findall('object') if any(m.get('key')=='name' and m.get('value','').lower()=='bed mount test 03 (0.325).stl' for m in o.findall('metadata'))]
        if len(candidates)!=1:raise SystemExit('Could not identify the OLD mount in the original complete assembly. Use Sources/..._Original.3mf.')
        target_id=candidates[0].get('id')
        target_build=next(i for i in target_builds if i.get('objectid')==target_id)
        component,target_path,model,obj,old_mesh,old_world=part(target,target_root,target_build)
        references=[c for c in target_root.findall('.//c:component',NS) if c.get(f'{{{PROD}}}path','').lstrip('/')==target_path and c.get('objectid')==component.get('objectid')]
        if len(references)!=1:raise SystemExit('The old mount mesh is shared; refusing to change other objects.')
        old_faces=len(old_mesh.findall('c:triangles/c:triangle',NS))
        source_lo,source_hi=bounds(source_world);target_lo,target_hi=bounds(old_world)
        if any(abs((source_hi[i]-source_lo[i])-(target_hi[i]-target_lo[i]))>1e-4 for i in range(3)):
            raise SystemExit('World-space mount envelopes differ; no scaling was applied.')
        shift=[(target_lo[i]+target_hi[i]-source_lo[i]-source_hi[i])/2 for i in range(3)]
        replacement=copy.deepcopy(source_mesh)
        for element,point in zip(replacement.findall('c:vertices/c:vertex',NS),source_world):
            desired=[point[i]+shift[i] for i in range(3)]
            local=inverse(inverse(desired,target_build.get('transform',IDENTITY)),component.get('transform',IDENTITY))
            element.attrib.update({axis:f'{value:.9f}' for axis,value in zip('xyz',local)})
        obj.remove(old_mesh);obj.append(replacement)
        name='Bed-Mount-Flat-A1-2026.stl'
        for meta in candidates[0].findall('.//metadata'):
            if meta.get('key')=='name':meta.set('value',name)
            if meta.get('key','').startswith('source_offset_'):meta.set('value','0')
            if 'face_count' in meta.attrib:meta.set('face_count',str(source_faces))
        for stat in candidates[0].findall('.//mesh_stat'):stat.set('face_count',str(source_faces))
        for plate in settings.findall('plate'):
            for meta in list(plate):
                if meta.tag=='metadata' and meta.get('key') in {'gcode_file','thumbnail_file','thumbnail_no_light_file','top_file','pick_file'}:plate.remove(meta)
        for meta in list(target_root):
            if meta.tag==f'{{{CORE}}}metadata' and meta.get('name') in {'Thumbnail_Middle','Thumbnail_Small','DesignerCover','ProfileCover'}:target_root.remove(meta)
        updates={'Title':'A1 Bed Dragchain - conector PLANO 2026',
                 'Description':'Complete RV01 assembly updated with the flat 2026 mount from the supplied standalone obj_42+bed+mount.3mf. The old bulky mount is replaced; all other assembly meshes and part placements are preserved. Original design: Kar Fai. Compatibility selection supplied by the maintainer.',
                 'ProfileTitle':'RV01 - conector plano A1 2026','ModificationDate':date.today().isoformat(),'Origin':'modified'}
        for meta in target_root.findall('c:metadata',NS):
            if meta.get('name') in updates:meta.text=updates[meta.get('name')]
        rels=ET.fromstring(target.read('_rels/.rels'))
        for rel in list(rels):
            if 'thumbnail' in rel.get('Type','').lower():rels.remove(rel)
        replacements={target_path:xml_bytes(model),'3D/3dmodel.model':xml_bytes(target_root),
                      'Metadata/model_settings.config':xml_bytes(settings),'_rels/.rels':xml_bytes(rels,True)}
        for member in target.namelist():
            if member.startswith('Metadata/plate_') and member.endswith('.json'):
                info=json.loads(target.read(member))
                for entry in info.get('bbox_objects',[]):
                    if entry.get('name','').lower()=='bed mount test 03 (0.325).stl':entry['name']=name
                info.pop('first_layer_time',None);replacements[member]=json.dumps(info).encode()
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED) as dst:
            for info in target.infolist():
                member=info.filename
                if member.startswith('Auxiliaries/') or member.lower().endswith(('.png','.webp')) or '.gcode' in member or member=='Metadata/slice_info.config':continue
                dst.writestr(member,replacements.get(member,target.read(member)))
    record={'direction':'single supplied flat 2026 mount -> complete original RV01 assembly',
            'flat_source_filename':args.source.name,'flat_source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),
            'original_assembly_filename':args.target.name,'original_assembly_sha256':hashlib.sha256(args.target.read_bytes()).hexdigest(),
            'replaced_object_id':target_id,'replaced_mesh_path':target_path,'original_mount_triangles':old_faces,
            'flat_2026_mount_triangles':source_faces,'assembly_objects_before':len(target_builds),'assembly_objects_after':len(target_builds),
            'world_dimensions_xyz_mm':[source_hi[i]-source_lo[i] for i in range(3)],'scaled':False,
            'all_build_placements_preserved':True,'output_filename':args.output.name}
    args.output.with_suffix('.replacement.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
