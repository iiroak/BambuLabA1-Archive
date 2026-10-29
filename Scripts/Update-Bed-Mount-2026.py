#!/usr/bin/env python3
"""Replace the single bed mount with the revised mount from the RV01 project.

Python 3.10+, standard library only. The source project is not imported as
additional parts: only its revised mount mesh replaces the target mesh.
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
IDENTITY=[1.,0.,0.,0.,1.,0.,0.,0.,1.]

def xml_bytes(root,relationships=False):
    ET.register_namespace('',REL if relationships else CORE)
    value=ET.tostring(root,encoding='UTF-8',xml_declaration=True)
    ET.register_namespace('',CORE)
    return value

def apply(point,transform):
    x,y,z=point;m=list(map(float,transform.split()))
    if len(m)!=12:raise ValueError('Expected a 3MF 3x4 transformation')
    return [x*m[0]+y*m[3]+z*m[6]+m[9],x*m[1]+y*m[4]+z*m[7]+m[10],x*m[2]+y*m[5]+z*m[8]+m[11]]

def bounds(vertices):
    return ([min(v[i] for v in vertices) for i in range(3)],[max(v[i] for v in vertices) for i in range(3)])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path,help='A1+bed+dragchain+RV01.3mf')
    parser.add_argument('target',type=Path,help='Original single-part obj_42+bed+mount.3mf')
    parser.add_argument('--output',type=Path,required=True,help='New destination 3MF')
    args=parser.parse_args()
    if args.output.exists():raise SystemExit('Choose a new output file.')
    with zipfile.ZipFile(args.source) as source,zipfile.ZipFile(args.target) as target:
        source_settings=ET.fromstring(source.read('Metadata/model_settings.config'))
        candidates=[o for o in source_settings.findall('object') if any(m.get('key')=='name' and m.get('value','').lower()=='bed mount test 03 (0.325).stl' for m in o.findall('metadata'))]
        if len(candidates)!=1:raise SystemExit('Could not identify exactly one revised bed mount.')
        source_id=candidates[0].get('id')
        source_root=ET.fromstring(source.read('3D/3dmodel.model'))
        source_parent=source_root.find(f"c:resources/c:object[@id='{source_id}']",NS)
        source_components=source_parent.findall('c:components/c:component',NS)
        source_builds=[i for i in source_root.findall('c:build/c:item',NS) if i.get('objectid')==source_id]
        if len(source_components)!=1 or len(source_builds)!=1:raise SystemExit('Unexpected source component structure.')
        source_component=source_components[0]
        source_path=source_component.get(f'{{{PROD}}}path').lstrip('/')
        source_model=ET.fromstring(source.read(source_path))
        source_object=source_model.find(f"c:resources/c:object[@id='{source_component.get('objectid')}']",NS)
        new_mesh=copy.deepcopy(source_object.find('c:mesh',NS))
        source_vertices=[[float(e.get(a)) for a in 'xyz'] for e in new_mesh.findall('c:vertices/c:vertex',NS)]
        transformed=[apply(apply(v,source_component.get('transform')),source_builds[0].get('transform')) for v in source_vertices]

        target_root=ET.fromstring(target.read('3D/3dmodel.model'))
        builds=target_root.findall('c:build/c:item',NS)
        if len(builds)!=1:raise SystemExit('The target must contain only the single old mount.')
        build=builds[0]
        parent=target_root.find(f"c:resources/c:object[@id='{build.get('objectid')}']",NS)
        components=parent.findall('c:components/c:component',NS)
        if len(components)!=1:raise SystemExit('The target must have one mesh component.')
        component=components[0]
        for transform in [build.get('transform'),component.get('transform')]:
            if any(abs(a-b)>1e-8 for a,b in zip(list(map(float,transform.split()))[:9],IDENTITY)):
                raise SystemExit('The single target mount must use identity rotation and scale.')
        target_path=component.get(f'{{{PROD}}}path').lstrip('/')
        target_model=ET.fromstring(target.read(target_path))
        old_object=target_model.find(f"c:resources/c:object[@id='{component.get('objectid')}']",NS)
        old_mesh=old_object.find('c:mesh',NS)
        old_vertices=[[float(e.get(a)) for a in 'xyz'] for e in old_mesh.findall('c:vertices/c:vertex',NS)]
        old_lo,old_hi=bounds(old_vertices);new_lo,new_hi=bounds(transformed)
        old_size=[b-a for a,b in zip(old_lo,old_hi)];new_size=[b-a for a,b in zip(new_lo,new_hi)]
        if any(abs(a-b)>1e-4 for a,b in zip(old_size,new_size)):
            raise SystemExit('Revised and original mount dimensions do not match; no scaling was applied.')
        delta=[(old_lo[i]+old_hi[i]-new_lo[i]-new_hi[i])/2 for i in range(3)]
        local=[[v[i]+delta[i] for i in range(3)] for v in transformed]
        for element,point in zip(new_mesh.findall('c:vertices/c:vertex',NS),local):
            element.attrib.update({axis:f'{value:.9f}' for axis,value in zip('xyz',point)})
        old_object.remove(old_mesh);old_object.append(new_mesh)
        face_count=len(new_mesh.findall('c:triangles/c:triangle',NS))
        new_name='BedMount_A1_2026_RV01.stl'
        settings=ET.fromstring(target.read('Metadata/model_settings.config'))
        for obj in settings.findall('object'):
            for meta in obj.findall('.//metadata'):
                if meta.get('key')=='name':meta.set('value',new_name)
                if meta.get('key','').startswith('source_offset_'):meta.set('value','0')
                if 'face_count' in meta.attrib:meta.set('face_count',str(face_count))
            for stat in obj.findall('.//mesh_stat'):stat.set('face_count',str(face_count))
        for plate in settings.findall('plate'):
            for meta in list(plate):
                if meta.tag=='metadata' and meta.get('key') in {'gcode_file','thumbnail_file','thumbnail_no_light_file','top_file','pick_file'}:plate.remove(meta)
        for item in settings.findall('assemble/assemble_item'):
            if item.get('instance_id') is not None:item.set('transform',build.get('transform'))
        for meta in list(target_root):
            if meta.tag==f'{{{CORE}}}metadata' and meta.get('name') in {'Thumbnail_Middle','Thumbnail_Small','ProfileCover','DesignerCover'}:target_root.remove(meta)
        updates={
            'Title':'A1 bed mount - conector 2026 - RV01',
            'Description':'Single bed mount updated with the revised bed mount test 03 (0.325).stl from the supplied A1+bed+dragchain+RV01.3mf. Original design Kar Fai. The mesh was reoriented without scaling and replaces the old mount; no chain links were added. A1 2026 compatibility specified by the maintainer.',
            'ModificationDate':date.today().isoformat(),'Origin':'modified',
            'ProfileTitle':'A1 2026 - bed mount actualizado RV01',
        }
        for meta in target_root.findall('c:metadata',NS):
            if meta.get('name') in updates:meta.text=updates[meta.get('name')]
        rels=ET.fromstring(target.read('_rels/.rels'))
        for rel in list(rels):
            if 'thumbnail' in rel.get('Type','').lower():rels.remove(rel)
        replacements={target_path:xml_bytes(target_model),'3D/3dmodel.model':xml_bytes(target_root),
                      'Metadata/model_settings.config':xml_bytes(settings),'_rels/.rels':xml_bytes(rels,True)}
        if 'Metadata/plate_1.json' in target.namelist():
            plate=json.loads(target.read('Metadata/plate_1.json'))
            world=[apply(v,build.get('transform')) for v in local]
            lo,hi=bounds(world);bbox=[*lo[:2],*hi[:2]]
            plate['bbox_all']=bbox
            for entry in plate.get('bbox_objects',[]):entry['name']=new_name;entry['bbox']=bbox
            plate.pop('first_layer_time',None)
            replacements['Metadata/plate_1.json']=json.dumps(plate).encode()
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED) as result:
            for info in target.infolist():
                name=info.filename
                if name.startswith('Auxiliaries/') or name.lower().endswith(('.png','.webp')) or '.gcode' in name or name=='Metadata/slice_info.config':continue
                result.writestr(name,replacements.get(name,target.read(name)))
    record={'source_filename':args.source.name,'source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),
            'original_target_filename':args.target.name,'original_target_sha256':hashlib.sha256(args.target.read_bytes()).hexdigest(),
            'source_object_id':source_id,'source_mesh_path':source_path,'source_mesh_name':'bed mount test 03 (0.325).stl',
            'target_mesh_path':target_path,'original_vertices':len(old_vertices),'original_triangles':len(old_mesh.findall('c:triangles/c:triangle',NS)),
            'replacement_vertices':len(local),'replacement_triangles':face_count,'dimensions_xyz_mm':new_size,
            'scaled':False,'target_build_transform':build.get('transform'),'output_filename':args.output.name}
    args.output.with_suffix('.replacement.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
