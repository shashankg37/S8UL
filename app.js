import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const canvas = document.querySelector('#pet-canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene(); scene.fog = new THREE.FogExp2(0x0a1721, .045);
const camera = new THREE.PerspectiveCamera(35, 1, .1, 100); camera.position.set(0, 2.2, 10);
const controls = new OrbitControls(camera, canvas); controls.enablePan=false; controls.enableZoom=false; controls.minAzimuthAngle=-.45; controls.maxAzimuthAngle=.45; controls.minPolarAngle=1.14; controls.maxPolarAngle=1.7; controls.target.set(0, 1.4, 0); controls.enableDamping=true;
const pet = new THREE.Group(); scene.add(pet);
const metal = new THREE.MeshStandardMaterial({color:0xf3e4cc,roughness:.28,metalness:.62});
const orange = new THREE.MeshStandardMaterial({color:0xf46214,roughness:.3,metalness:.25});
const red = new THREE.MeshStandardMaterial({color:0xe84225,roughness:.42,metalness:.15});
const dark = new THREE.MeshStandardMaterial({color:0x402418,roughness:.55});
const black = new THREE.MeshStandardMaterial({color:0x130c09,roughness:.4});
const glass = new THREE.MeshPhysicalMaterial({color:0xff9b36,roughness:.08,metalness:.1,transmission:.08,clearcoat:1});
function mesh(geo,mat,x,y,z,scale=1){const o=new THREE.Mesh(geo,mat);o.position.set(x,y,z);o.scale.setScalar(scale);o.castShadow=true;o.receiveShadow=true;pet.add(o);return o}
const body=mesh(new THREE.SphereGeometry(1.45,48,32),metal,0,1.75,0); body.scale.set(.86,1.05,.76);
const torso=mesh(new THREE.CylinderGeometry(1.06,1.16,1.7,48),metal,0,.95,0); torso.scale.z=.82;
const faceRing=mesh(new THREE.TorusGeometry(.76,.15,16,48),orange,0,2.13,1.16); faceRing.rotation.x=0;
const face=mesh(new THREE.SphereGeometry(.71,40,28),glass,0,2.13,1.17); face.scale.z=.24;
const leftEye=mesh(new THREE.SphereGeometry(.105,18,14),black,-.25,2.25,1.42);leftEye.scale.z=.35;
const rightEye=mesh(new THREE.SphereGeometry(.105,18,14),black,.25,2.25,1.42);rightEye.scale.z=.35;
const mouth=mesh(new THREE.TorusGeometry(.16,.055,10,22,Math.PI),black,0,1.96,1.42);mouth.rotation.z=Math.PI;mouth.scale.z=.32;
const helmet=mesh(new THREE.SphereGeometry(1.48,48,32),metal,0,2.13,0);helmet.scale.set(.88,1.02,.78);helmet.material=metal;
const visorCut = new THREE.Mesh(new THREE.SphereGeometry(.86,40,28), new THREE.MeshBasicMaterial({color:0x0b1721}));visorCut.position.set(0,2.13,1.12);visorCut.scale.set(1,1,.18);pet.add(visorCut);
const cone=mesh(new THREE.ConeGeometry(.9,1.25,40),red,0,3.64,0);cone.scale.z=.85;
const collar=mesh(new THREE.TorusGeometry(1.08,.11,12,40),orange,0,1.23,0);collar.rotation.x=Math.PI/2;
const cape=new THREE.Mesh(new THREE.PlaneGeometry(2.2,2.45,8,8),red);cape.position.set(.72,1.55,-.58);cape.rotation.y=-.55;cape.rotation.x=.08;pet.add(cape);
const arms=[]; for(const side of [-1,1]){const arm=mesh(new THREE.CapsuleGeometry(.28,.75,8,16),metal,side*1.3,1.2,.05);arm.rotation.z=side*-.48;arms.push(arm);const glove=mesh(new THREE.SphereGeometry(.34,20,16),orange,side*1.62,.7,.3);glove.scale.set(1,.9,.82);}
for(const side of [-1,1]){const leg=mesh(new THREE.CapsuleGeometry(.34,.46,8,16),metal,side*.55,.0,0);const boot=mesh(new THREE.SphereGeometry(.48,22,16),orange,side*.55,-.4,.23);boot.scale.set(1, .68, 1.25)}
const pack=mesh(new THREE.CylinderGeometry(.38,.44,1.35,24),dark,1.12,1.3,-.45);pack.rotation.z=-.22;const flame=mesh(new THREE.ConeGeometry(.18,.65,16),orange,1.38,.5,-.5);flame.rotation.z=-.65;
const badge=mesh(new THREE.CircleGeometry(.20,24),red,.7,1.45,.74);badge.rotation.y=0;
const ground=new THREE.Mesh(new THREE.CylinderGeometry(2.3,2.55,.35,40),new THREE.MeshStandardMaterial({color:0x14232c,roughness:.9,metalness:.05}));ground.position.y=-.75;ground.receiveShadow=true;scene.add(ground);
const light=new THREE.HemisphereLight(0x84d8ed,0x19202a,2.5);scene.add(light);const key=new THREE.DirectionalLight(0xffd8a8,4);key.position.set(-5,7,5);key.castShadow=true;scene.add(key);const rim=new THREE.PointLight(0xff5f1f,12,12);rim.position.set(3,2,-2);scene.add(rim);
let mode='happy', t=0, fuel=86;
const status={happy:'Ready for the next mission.',excited:'Rocket is fired up! Let’s go!',focused:'Mission control engaged. Eyes forward.',sleepy:'Low power… a tiny nap sounds nice.'};
function setMode(next){mode=next;document.querySelectorAll('[data-mood]').forEach(b=>b.classList.toggle('active',b.dataset.mood===next));document.querySelector('#moodValue').textContent=next.toUpperCase();document.querySelector('#statusText').textContent=status[next];document.querySelector('#speech').innerHTML= next==='sleepy'?'Zzz… wake me for something important. <span>☾</span>':next==='focused'?'Target locked. Let’s make it count. <span>✦</span>':next==='excited'?'YES! Full thrusters! <span>⚡</span>':'Yo! Ready to crush the day? <span>✦</span>';}
document.querySelectorAll('[data-mood]').forEach(b=>b.onclick=()=>setMode(b.dataset.mood));
document.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>{const map={focus:'focused',rest:'sleepy',break:'happy',cheer:'excited'};fuel=Math.min(100,fuel+(b.dataset.action==='rest'?9:2));document.querySelector('#fuel').textContent=fuel+'%';document.querySelector('#fuelBar').style.width=fuel+'%';setMode(map[b.dataset.action]);});
canvas.addEventListener('dblclick',()=>setMode(mode==='happy'?'excited':'happy'));
function resize(){const w=canvas.clientWidth,h=canvas.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}addEventListener('resize',resize);resize();
function animate(ms){requestAnimationFrame(animate);t=ms*.001; const bounce=mode==='excited'?.18:mode==='sleepy'?.035:.075;pet.position.y=Math.sin(t*(mode==='excited'?6:2))*bounce;pet.rotation.y=Math.sin(t*.7)*.09;cape.rotation.z=-.09+Math.sin(t*3)*.045;arms[0].rotation.z=-.48+Math.sin(t*2)*.08;arms[1].rotation.z=.48-Math.sin(t*2)*.08;if(mode==='focused'){leftEye.scale.y=.55;rightEye.scale.y=.55}else if(mode==='sleepy'){leftEye.scale.y=.15;rightEye.scale.y=.15}else{leftEye.scale.y=1;rightEye.scale.y=1}controls.update();renderer.render(scene,camera)}requestAnimationFrame(animate);
function updateClock(){document.querySelector('#clock').textContent=new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}updateClock();setInterval(updateClock,1000);
