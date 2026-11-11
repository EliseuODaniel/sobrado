"""Ajuste local por pontos de imagem aproximados, sem promover escala a medida real."""
from pathlib import Path
import json
import math
import numpy as np
from scipy.optimize import least_squares

root=Path(__file__).resolve().parents[1];path=root/'config/planta-casa.json';cfg=json.loads(path.read_text());width,height=1200,630
def project(params,points):
    x,y,z,yaw,pitch,lens=params
    forward=np.array([math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),math.sin(pitch)])
    right=np.array([math.cos(yaw),-math.sin(yaw),0]);up=np.cross(right,forward);delta=np.asarray(points)-[x,y,z];depth=delta@forward
    return np.stack([(0.5+(lens/36)*(delta@right)/depth)*width,(0.5-(lens/36)*(width/height)*(delta@up)/depth)*height],axis=1)
jobs={
 'CAM_Foto_Sala_Frente':{
  'photo':'sala4.webp',
  'labels':['TV centro','porta lavabo centro','porta entrada centro','janela frontal centro aproximado','primeiro degrau centro aproximado'],
  'world':[[2.985,1.85,1.60],[3.15,3.185,1.05],[2.675,.02,1.05],[1.19,.075,1.50],[3.44,4.18,.161]],
  'pixels':[[511,315],[265,350],[680,337],[930,310],[135,545]],
  'bounds':([.6,5.0,1.2,2.65,-.16,14],[2.7,7.5,1.9,3.5,.14,32])},
 'CAM_Foto_Sala_Fundos':{
  'photo':'sala7.webp',
  'labels':['espelho centro','mesa jantar tampo centro','armário bar centro','TV borda afastada centro'],
  'world':[[.085,4.25,1.85],[1.52,6.00,.792],[1.88,8.46,2.17],[2.985,2.65,1.60]],
  'pixels':[[344,262],[568,423],[600,265],[900,365]],
  'bounds':([.8,.20,1.2,-.20,-.16,14],[1.95,1.0,1.9,.20,.12,30])}
}
reports={}
for name,job in jobs.items():
    c=cfg['cameras'][name];delta=np.array(c['target'])-c['position'];yaw=math.atan2(delta[0],delta[1]);pitch=math.atan2(delta[2],np.linalg.norm(delta[:2]));start=np.array([*c['position'],yaw,pitch,c['lens']])
    lower,upper=map(np.asarray,job['bounds']);start=np.clip(start,lower+1e-6,upper-1e-6);targets=np.asarray(job['pixels'])
    def residual(p):
        pixels=project(p,job['world']);errors=(pixels-targets)/[width,height]
        return np.concatenate([errors.ravel(),[(p[2]-1.6)*.03,(p[5]-22)*.001]])
    result=least_squares(residual,start,bounds=(lower,upper),loss='soft_l1',f_scale=.05,max_nfev=2500)
    p=result.x;forward=np.array([math.sin(p[3])*math.cos(p[4]),math.cos(p[3])*math.cos(p[4]),math.sin(p[4])]);c.update(position=[float(v) for v in p[:3]],target=[float(v) for v in p[:3]+forward*7],lens=float(p[5]))
    before=project(start,job['world']);after=project(p,job['world']);reports[name]={'source':job['photo'],'classification':'pontos aproximados selecionados pelo agente; não é calibração métrica','labels':job['labels'],'observed_pixels':job['pixels'],'before_pixels':before.tolist(),'after_pixels':after.tolist(),'rms_before_px':float(np.sqrt(np.mean((before-targets)**2))),'rms_after_px':float(np.sqrt(np.mean((after-targets)**2))),'camera':c}
path.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n');(root/'relatorios/revisao-02/ajuste-cameras.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
for name,r in reports.items():print(name,round(r['rms_before_px'],1),'->',round(r['rms_after_px'],1),'pixels RMS (marcos aproximados)')
