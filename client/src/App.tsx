import { useEffect, useState } from 'react'

function App() {

  const [health, setHealth] = useState('unknown');

  const getHealth = async() => {
    let health = 'unknown'
    const response = await fetch('/api/health')
    const data = await response.json()
    health = data.status == 'ok' ? 'healthy' : data.status
    return health;
  }

  useEffect(() => {
    getHealth().then((health) => setHealth(health));
  }, []);

  return (
    <>
      <p>Api status: {health}</p>
    </>
  )
}

export default App
