import { useEffect, useState } from 'react'
import { Cloud, CloudRain, Sun, Wind, Droplets, Calendar } from 'lucide-react'
import { weatherAPI } from '../services/api'
import toast from 'react-hot-toast'

const Forecast = () => {
  const [forecasts, setForecasts] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [selectedCity, setSelectedCity] = useState('Mumbai')

  const cities = [
    { name: 'Mumbai', lat: 19.0760, lon: 72.8777 },
    { name: 'Delhi', lat: 28.6139, lon: 77.2090 },
    { name: 'Chennai', lat: 13.0827, lon: 80.2707 },
    { name: 'Bangalore', lat: 12.9716, lon: 77.5946 },
    { name: 'Kolkata', lat: 22.5726, lon: 88.3639 },
    { name: 'Hyderabad', lat: 17.3850, lon: 78.4867 },
    { name: 'Pune', lat: 18.5204, lon: 73.8567 },
  ]

  useEffect(() => {
    loadForecasts()
  }, [])

  const loadForecasts = async () => {
    setLoading(true)
    const newForecasts: any = {}

    try {
      // Load forecast for all cities
      for (const city of cities) {
        try {
          const response = await weatherAPI.getForecast(city.lat, city.lon, 7)
          newForecasts[city.name] = response.data
        } catch (error) {
          console.error(`Failed to load forecast for ${city.name}`)
        }
      }
      setForecasts(newForecasts)
    } catch (error) {
      toast.error('Failed to load forecasts')
    } finally {
      setLoading(false)
    }
  }

  const getWeatherIcon = (description: string) => {
    const desc = description?.toLowerCase() || ''
    if (desc.includes('rain') || desc.includes('shower')) return <CloudRain className="w-8 h-8 text-blue-500" />
    if (desc.includes('cloud')) return <Cloud className="w-8 h-8 text-gray-500" />
    if (desc.includes('clear') || desc.includes('sun')) return <Sun className="w-8 h-8 text-yellow-500" />
    return <Cloud className="w-8 h-8 text-gray-400" />
  }

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    } catch {
      return dateStr
    }
  }

  const selectedForecast = forecasts[selectedCity]
  const forecastData = selectedForecast?.dailyForecasts?.forecastLocation?.forecast || []

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading forecasts...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">7-Day Weather Forecast</h1>
        <p className="text-gray-600">Real-time weather predictions from HERE Weather API</p>
      </div>

      {/* City Selector */}
      <div className="mb-6 flex gap-2 flex-wrap">
        {cities.map((city) => (
          <button
            key={city.name}
            onClick={() => setSelectedCity(city.name)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedCity === city.name
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            {city.name}
          </button>
        ))}
      </div>

      {/* Current City Info */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{selectedCity}</h2>
            <p className="text-blue-100">7-Day Weather Forecast</p>
          </div>
          <Calendar className="w-12 h-12 text-blue-200" />
        </div>
      </div>

      {/* Forecast Cards */}
      {forecastData.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4">
          {forecastData.slice(0, 7).map((day: any, index: number) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow"
            >
              {/* Date */}
              <div className="text-center mb-3">
                <p className="text-sm font-semibold text-gray-900">
                  {day.weekday || formatDate(day.utcTime)}
                </p>
                <p className="text-xs text-gray-500">{formatDate(day.utcTime)}</p>
              </div>

              {/* Weather Icon */}
              <div className="flex justify-center mb-3">
                {getWeatherIcon(day.description || day.skyDescription)}
              </div>

              {/* Temperature */}
              <div className="text-center mb-3">
                <div className="flex items-center justify-center gap-2">
                  <span className="text-2xl font-bold text-gray-900">
                    {day.highTemperature ? Math.round(parseFloat(day.highTemperature)) : '--'}°
                  </span>
                </div>
                <div className="text-xs text-gray-500">
                  Low: {day.lowTemperature ? Math.round(parseFloat(day.lowTemperature)) : '--'}°
                </div>
              </div>

              {/* Description */}
              <p className="text-xs text-center text-gray-600 mb-3 line-clamp-2">
                {day.description || day.skyDescription || 'No description'}
              </p>

              {/* Additional Info */}
              <div className="space-y-2 border-t border-gray-100 pt-3">
                {/* Rain Probability */}
                {day.precipitationProbability !== undefined && day.precipitationProbability !== null && (
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1 text-gray-600">
                      <CloudRain className="w-3 h-3" />
                      <span>Rain</span>
                    </div>
                    <span className="font-semibold text-blue-600">{day.precipitationProbability}%</span>
                  </div>
                )}

                {/* Humidity */}
                {day.humidity !== undefined && day.humidity !== null && (
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1 text-gray-600">
                      <Droplets className="w-3 h-3" />
                      <span>Humidity</span>
                    </div>
                    <span className="font-semibold">{day.humidity}%</span>
                  </div>
                )}

                {/* Wind */}
                {day.windSpeed !== undefined && day.windSpeed !== null && (
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1 text-gray-600">
                      <Wind className="w-3 h-3" />
                      <span>Wind</span>
                    </div>
                    <span className="font-semibold">{Math.round(parseFloat(day.windSpeed))} km/h</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <Cloud className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No forecast data available for {selectedCity}</p>
          <button
            onClick={loadForecasts}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Data Source */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500">
          Data provided by <span className="font-semibold">HERE Weather API</span> • Updated in real-time
        </p>
      </div>
    </div>
  )
}

export default Forecast
