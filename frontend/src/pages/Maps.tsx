import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import { weatherAPI } from '../services/api'
import toast from 'react-hot-toast'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default markers
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

const Maps = () => {
  const [weatherImpact, setWeatherImpact] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const [activeLayers, setActiveLayers] = useState({
    traffic: false,
    weather: false
  })

  useEffect(() => {
    loadMapData()
  }, [])

  const loadMapData = async () => {
    try {
      const impactRes = await weatherAPI.getWeatherImpact()
      setWeatherImpact(impactRes.data)
    } catch (error) {
      toast.error('Failed to load map data')
    } finally {
      setLoading(false)
    }
  }

  const toggleLayer = (layer: 'traffic' | 'weather') => {
    setActiveLayers(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }))
  }

  const getCityStatusColor = (status: string) => {
    switch (status) {
      case 'Critical':
        return '#dc2626'
      case 'Alert':
        return '#f59e0b'
      case 'Warning':
        return '#eab308'
      default:
        return '#10b981'
    }
  }

  // City coordinates
  const getCityCoordinates = (cityName: string): [number, number] => {
    const coords: any = {
      'Mumbai': [19.0760, 72.8777],
      'Pune': [18.5204, 73.8567],
      'Bangalore': [12.9716, 77.5946],
      'Delhi': [28.6139, 77.2090],
      'Hyderabad': [17.3850, 78.4867],
      'Chennai': [13.0827, 80.2707],
      'Kolkata': [22.5726, 88.3639],
    }
    return coords[cityName] || [20.5937, 78.9629]
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="flex h-full">
      {/* Map Container */}
      <div className="flex-1 relative">
        <MapContainer
          center={[20.5937, 78.9629]}
          zoom={5}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Weather Incidents Layer - Circle markers for each city */}
          {activeLayers.weather && weatherImpact?.city_breakdown?.map((city: any) => {
            const [lat, lon] = getCityCoordinates(city.city)
            return (
              <Circle 
                key={`weather-${city.city}`} 
                center={[lat, lon]}
                radius={50000}
                pathOptions={{
                  color: '#3b82f6',
                  fillColor: '#3b82f6',
                  fillOpacity: 0.3,
                }}
              >
                <Popup>
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-lg text-gray-900">{city.city}</h3>
                      <span className={`px-2 py-1 text-xs font-bold rounded $
                        ${city.status === 'Critical' ? 'bg-red-500 text-white' :
                          city.status === 'Alert' ? 'bg-orange-500 text-white' :
                          city.status === 'Warning' ? 'bg-yellow-500 text-gray-900' :
                          'bg-green-500 text-white'
                        }`
                      }>
                        {city.status}
                      </span>
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      <p className="text-sm text-gray-700">
                        <span className="font-semibold">Weather Conditions</span>
                      </p>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>🌡️ {city.temperature}°C</div>
                        <div>💧 {city.humidity}%</div>
                        <div>💨 {city.windspeed ? `${city.windspeed} km/h` : 'N/A'}</div>
                        <div>🌧️ {city.rain_alert ? 'Heavy Rain' : 'Clear'}</div>
                      </div>
                    </div>

                    <div className="text-xs text-gray-600">
                      Weather data from HERE API
                    </div>
                  </div>
                </Popup>
              </Circle>
            )
          })}

          {/* Traffic Incidents - City Level Markers */}
          {activeLayers.traffic && weatherImpact?.city_breakdown?.map((city: any) => {
            const [lat, lon] = getCityCoordinates(city.city)
            return (
              <Marker 
                key={city.city} 
                position={[lat, lon]}
                icon={L.divIcon({
                  html: `<div style="background-color: ${getCityStatusColor(city.status)}; width: 40px; height: 40px; border-radius: 50%; border: 3px solid white; display: flex; align-items: center; justify-center; font-weight: bold; color: white; font-size: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">${city.traffic_count}</div>`,
                  className: '',
                  iconSize: [40, 40],
                  iconAnchor: [20, 20],
                })}
              >
                <Popup maxWidth={400}>
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-lg text-gray-900">{city.city}</h3>
                      <span className={`px-2 py-1 text-xs font-bold rounded ${
                        city.status === 'Critical' ? 'bg-red-500 text-white' :
                        city.status === 'Alert' ? 'bg-orange-500 text-white' :
                        city.status === 'Warning' ? 'bg-yellow-500 text-gray-900' :
                        'bg-green-500 text-white'
                      }`}>
                        {city.status}
                      </span>
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      <p className="text-sm text-gray-700">
                        <span className="font-semibold">{city.traffic_count} Critical Incidents</span>
                      </p>
                      <p className="text-xs text-gray-600">
                        🌡️ {city.temperature}°C | 💧 {city.humidity}% | 
                        {city.rain_alert ? ' 🌧️ Rain Alert' : ' ☀️ Clear'}
                      </p>
                    </div>

                    {city.traffic_incidents && city.traffic_incidents.length > 0 && (
                      <div className="border-t pt-3">
                        <p className="text-xs font-bold text-gray-900 mb-2">Road Closures & Accidents:</p>
                        <div className="max-h-48 overflow-y-auto space-y-2">
                          {city.traffic_incidents.map((incident: any, idx: number) => (
                            <div key={idx} className="text-xs bg-gray-50 p-2 rounded border-l-2 border-red-400">
                              <p className="font-semibold text-gray-900">
                                {incident.road_closed ? '🚧 ROAD CLOSED' : '⚠️ CRITICAL'}: {incident.type}
                              </p>
                              <p className="text-gray-700">{incident.description}</p>
                              {incident.start_time && (
                                <p className="text-gray-500 mt-1">
                                  Since: {new Date(incident.start_time).toLocaleString()}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                  </div>
                </Popup>
              </Marker>
            )
          })}
        </MapContainer>
      </div>

      {/* Sidebar */}
      <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto">
        <div className="p-6 space-y-6">
          {/* Layer Controls */}
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Map Layers</h3>
            <div className="space-y-3">
              <label className={`flex items-center justify-between p-3 rounded-lg cursor-pointer border-2 transition-all $
                ${activeLayers.traffic ? 'bg-orange-50 border-orange-500' : 'bg-gray-50 border-gray-200 hover:border-gray-300'}`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-orange-600 rounded-full"></div>
                  <div>
                    <p className="font-semibold text-gray-900">Traffic Incidents</p>
                    <p className="text-xs text-gray-600">🚗 7 Cities - LIVE from HERE</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={activeLayers.traffic}
                  onChange={() => toggleLayer('traffic')}
                  className="w-4 h-4"
                />
              </label>

              <label className={`flex items-center justify-between p-3 rounded-lg cursor-pointer border-2 transition-all $
                ${activeLayers.weather ? 'bg-blue-50 border-blue-500' : 'bg-gray-50 border-gray-200 hover:border-gray-300'}`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                  <div>
                    <p className="font-semibold text-gray-900">Weather Incidents</p>
                    <p className="text-xs text-gray-600">🌦️ 7 Cities - LIVE from HERE</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={activeLayers.weather}
                  onChange={() => toggleLayer('weather')}
                  className="w-4 h-4"
                />
              </label>
            </div>
          </div>

          {/* Traffic Cities Info */}
          {weatherImpact && (
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-4">City Traffic Status</h3>
              <div className="space-y-2">
                {weatherImpact.city_breakdown?.map((city: any) => (
                  <div key={city.city} className={`p-3 rounded-lg border-l-4 ${
                    city.status === 'Critical' ? 'bg-red-50 border-red-500' :
                    city.status === 'Alert' ? 'bg-orange-50 border-orange-500' :
                    city.status === 'Warning' ? 'bg-yellow-50 border-yellow-500' :
                    'bg-green-50 border-green-500'
                  }`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-gray-900">{city.city}</span>
                      <span className="text-xs font-bold text-gray-700">{city.traffic_count} issues</span>
                    </div>
                    <p className="text-xs text-gray-600">{city.status} status</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Maps
