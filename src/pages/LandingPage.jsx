import { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, useTexture } from '@react-three/drei';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const Earth = () => {
  const earthRef = useRef();
  const cloudsRef = useRef();

  const [colorMap, normalMap, cloudsMap] = useTexture([
    'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg',
    'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_normal_2048.jpg',
    'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_clouds_1024.png'
  ]);

  useFrame(() => {
    if (earthRef.current) {
      earthRef.current.rotation.y += 0.001;
    }
    if (cloudsRef.current) {
      cloudsRef.current.rotation.y += 0.0012;
    }
  });

  return (
    <group>
      <mesh ref={earthRef}>
        <sphereGeometry args={[2.5, 64, 64]} />
        <meshStandardMaterial 
          map={colorMap} 
          normalMap={normalMap} 
          roughness={0.7} 
          metalness={0.1}
        />
      </mesh>
      <mesh ref={cloudsRef}>
        <sphereGeometry args={[2.52, 64, 64]} />
        <meshStandardMaterial 
          map={cloudsMap}
          transparent={true}
          opacity={0.4}
          blending={2}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
};



const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      <div className="canvas-container">
        <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
          <ambientLight intensity={1.5} />
          <pointLight position={[10, 10, 10]} intensity={2.5} />
          <directionalLight position={[-10, 0, -5]} intensity={0.5} color="#ffffff" />
          <Suspense fallback={null}>
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
            <Earth />
          </Suspense>
          <OrbitControls 
            enableZoom={false} 
            enablePan={false} 
            rotateSpeed={0.5}
            autoRotate
            autoRotateSpeed={0.5}
          />
        </Canvas>
      </div>

      <div className="hero-content">
        <h1 className="hero-title animate-fade-in text-gradient">GaiaOS</h1>
        <h2 className="hero-subtitle animate-fade-in" style={{ animationDelay: '0.2s' }}>
          Earth Digital Twin AI
        </h2>
        <p className="hero-description animate-fade-in" style={{ animationDelay: '0.4s' }}>
          A unified artificial intelligence system that models Earth's<br/>
          environmental and urban systems using satellite data,<br/>
          climate records, and machine learning.
        </p>

        <div className="action-buttons animate-fade-in" style={{ animationDelay: '0.6s' }}>
          <button className="btn btn-primary" onClick={() => navigate('/explore')}>
            Enter System
          </button>
          <button className="btn btn-outline" onClick={() => navigate('/dashboard')}>
            Explore Predictions
          </button>
          <button className="btn btn-outline" onClick={() => navigate('/research')}>
            Research
          </button>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
