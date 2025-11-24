import React, {useState} from 'react'

export default function App(){
  const [health, setHealth] = useState(null)
  const [eventId, setEventId] = useState(null)

  async function checkHealth(){
    const r = await fetch('http://localhost:8080/api/health-all')
    const j = await r.json()
    setHealth(j)
  }

  async function fetchEvent(){
    const r = await fetch('http://localhost:8080/api/get-event-id', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ tournament_name: 'climax-2025-the-last-bite', event_name: 'smash-bros-ultimate-singles' })
    })
    const j = await r.json()
    setEventId(j)
  }

  return (
    <div style={{padding:20,fontFamily:'Arial'}}>
      <h1>Proyecto Microservicios - Frontend</h1>
      <div style={{marginBottom:10}}>
        <button onClick={checkHealth}>Check Health All</button>
        <button onClick={fetchEvent} style={{marginLeft:10}}>Get Event ID</button>
      </div>

      <div>
        <h3>Health</h3>
        <pre style={{background:'#f7f7f7',padding:10}}>{health?JSON.stringify(health,null,2):'No data'}</pre>
      </div>

      <div>
        <h3>Event ID</h3>
        <pre style={{background:'#f7f7f7',padding:10}}>{eventId?JSON.stringify(eventId,null,2):'No data'}</pre>
      </div>
    </div>
  )
}
