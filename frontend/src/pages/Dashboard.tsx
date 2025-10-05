import { useEffect, useState } from 'react'
import { Activity, Users, Shield, MapPin, AlertTriangle, X } from 'lucide-react'
import { dashboardAPI, weatherAPI } from '../services/api'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [stats, setStats] = useState<any>(null)
  const [recentAlerts, setRecentAlerts] = useState<any[]>([])
  const [weatherImpact, setWeatherImpact] = useState<any>(null)
  const [selectedCity, setSelectedCity] = useState<any>(null)
  const [statDetailModal, setStatDetailModal] = useState<string | null>(null)
  const [expandedTraffic, setExpandedTraffic] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [statsRes, liveAlertsRes, impactRes] = await Promise.all([
        dashboardAPI.getStats(),
        weatherAPI.getIndiaAlerts(),  // LIVE weather alerts
        weatherAPI.getWeatherImpact()  // LIVE weather impact analysis
      ])
      setStats(statsRes.data)
      setWeatherImpact(impactRes.data)
      
      // Format live alerts to match expected structure
      const formattedAlerts = liveAlertsRes.data.alerts.map((alert: any) => ({
        id: `live-${alert.latitude}-${alert.longitude}`,
        title: alert.title === "4" ? `Heavy Rain Warning - ${alert.location}` : alert.title,
        category: alert.category,
        severity: alert.severity,
        location: alert.location,
        description: alert.description,
        action_required: alert.action_required,
        affected_population: 0,  // Live weather alerts don't have this data
        created_at: new Date().toISOString(),
        time_ago: 'Just now',
        source: 'LIVE - HERE Weather API'
      }))
      
      setRecentAlerts(formattedAlerts)
    } catch (error) {
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    toast.loading('Refreshing live data...', { id: 'refresh' })
    try {
      await loadDashboardData()
      toast.success('Data refreshed successfully!', { id: 'refresh' })
    } catch (error) {
      toast.error('Failed to refresh data', { id: 'refresh' })
    } finally {
      setRefreshing(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-700 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-700 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Emergency Dashboard</h1>
          <p className="text-gray-500 mt-1">Real-time disaster intelligence and response coordination</p>
        </div>
        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Activity className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      {/* Stats Grid - LIVE from HERE API */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Cities Monitored - FIRST */}
        <div 
          onClick={() => setStatDetailModal('cities')}
          className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-300 cursor-pointer hover:shadow-lg transition-all"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-700 font-semibold">Cities Tracked</h3>
            <Shield className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <p className="text-4xl font-bold text-purple-600">
              {weatherImpact?.cities_monitored || 0}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              {weatherImpact?.city_breakdown?.filter((c: any) => c.status !== 'Normal').length || 0} need attention
            </p>
            <p className="text-xs text-blue-600 mt-2 font-medium">Click for details →</p>
          </div>
        </div>

        {/* Weather Alerts */}
        <div 
          onClick={() => setStatDetailModal('weather')}
          className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-6 border-2 border-orange-300 cursor-pointer hover:shadow-lg transition-all"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-700 font-semibold">Weather Alerts</h3>
            <AlertTriangle className="w-6 h-6 text-orange-600" />
          </div>
          <div>
            <p className="text-4xl font-bold text-orange-600">
              {weatherImpact?.rain_alerts || 0}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              {weatherImpact?.critical_zones || 0} critical zones
            </p>
            <p className="text-xs text-blue-600 mt-2 font-medium">Click for details →</p>
          </div>
        </div>

        {/* Traffic Disruptions */}
        <div 
          onClick={() => setStatDetailModal('traffic')}
          className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-300 cursor-pointer hover:shadow-lg transition-all"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-700 font-semibold">Traffic Issues</h3>
            <Users className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p className="text-4xl font-bold text-blue-600">
              {weatherImpact?.traffic_disruptions || 0}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              Road closures & accidents
            </p>
            <p className="text-xs text-blue-600 mt-2 font-medium">Click for details →</p>
          </div>
        </div>

        {/* Overall Severity */}
        <div 
          onClick={() => setStatDetailModal('severity')}
          className={`rounded-xl p-6 border-2 cursor-pointer hover:shadow-lg transition-all ${
            weatherImpact?.severity_index === 'Critical' ? 'bg-gradient-to-br from-red-50 to-red-100 border-red-400' :
            weatherImpact?.severity_index === 'High' ? 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-400' :
            weatherImpact?.severity_index === 'Medium' ? 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-400' :
            'bg-gradient-to-br from-green-50 to-green-100 border-green-400'
          }`}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-700 font-semibold">Severity Level</h3>
            <MapPin className="w-6 h-6 text-gray-700" />
          </div>
          <div>
            <p className={`text-4xl font-bold ${
              weatherImpact?.severity_index === 'Critical' ? 'text-red-700' :
              weatherImpact?.severity_index === 'High' ? 'text-orange-700' :
              weatherImpact?.severity_index === 'Medium' ? 'text-yellow-700' :
              'text-green-700'
            }`}>
              {weatherImpact?.severity_index || 'Low'}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              Real-time analysis
            </p>
            <p className="text-xs text-blue-600 mt-2 font-medium">Click for details →</p>
          </div>
        </div>
      </div>

      {/* Recent Alerts and Response Efficiency */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Recent Alerts</h2>
            <p className="text-sm text-gray-500 mt-1">Latest emergency notifications and updates</p>
          </div>
          <div className="divide-y divide-gray-200">
            {recentAlerts.length > 0 ? (
              recentAlerts.map((alert) => (
                <div key={alert.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-1 text-xs font-semibold rounded border ${getSeverityColor(alert.severity)}`}>
                          {alert.severity}
                        </span>
                        <span className="text-sm font-medium text-gray-900">{alert.category}</span>
                        {alert.action_required && (
                          <span className="px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-700 border border-blue-200 rounded">
                            Action Required
                          </span>
                        )}
                      </div>
                      <h3 className="font-semibold text-gray-900 mb-1">{alert.title}</h3>
                      <p className="text-sm text-gray-600 mb-2">{alert.description}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>📍 {alert.location}</span>
                        <span>⏱️ {alert.time_ago}</span>
                        {alert.affected_population && (
                          <span>👥 {alert.affected_population.toLocaleString()} affected</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-12 text-center text-gray-500">
                No recent alerts
              </div>
            )}
          </div>
        </div>

        {/* Live Weather Impact */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border-2 border-blue-300">
          <div className="p-6 border-b border-blue-200 bg-white/50">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Live Weather Impact</h2>
                <p className="text-sm text-blue-600 mt-1 font-medium">Real-time data from HERE API</p>
              </div>
              <div className="px-3 py-1 bg-blue-600 text-white text-xs font-bold rounded-full animate-pulse">
                LIVE
              </div>
            </div>
          </div>
          <div className="p-6">
            {weatherImpact ? (
              <>
                {/* City-Wise Breakdown */}
                {weatherImpact.city_breakdown && weatherImpact.city_breakdown.length > 0 && (
                  <div>
                    <div className="space-y-2">
                      {weatherImpact.city_breakdown.map((city: any) => (
                        <div 
                          key={city.city} 
                          onClick={() => setSelectedCity(city)}
                          className="bg-white rounded-lg p-3 shadow-sm border-l-4 cursor-pointer hover:shadow-md transition-all" 
                          style={{
                            borderLeftColor: 
                              city.status === 'Critical' ? '#dc2626' : 
                              city.status === 'Alert' ? '#f59e0b' : 
                              city.status === 'Warning' ? '#eab308' : '#10b981'
                          }}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-semibold text-gray-900">{city.city}</span>
                            <span className={`text-xs font-bold px-2 py-1 rounded ${
                              city.status === 'Critical' ? 'bg-red-100 text-red-700' :
                              city.status === 'Alert' ? 'bg-orange-100 text-orange-700' :
                              city.status === 'Warning' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              {city.status}
                            </span>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                            <div>🌡️ {city.temperature ? `${city.temperature}°C` : 'N/A'}</div>
                            <div>💧 {city.humidity ? `${city.humidity}%` : 'N/A'}</div>
                            <div>{city.rain_alert ? '🌧️ Rain Alert' : '☀️ Clear'}</div>
                            <div>🚗 {city.traffic_count} incidents</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-blue-200 text-center mt-4">
                  <p className="text-xs text-gray-600">
                    Monitoring <span className="font-bold">{weatherImpact.cities_monitored} cities</span> across India
                  </p>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-sm text-gray-600 mt-2">Loading impact data...</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stat Detail Modals */}
      {statDetailModal && weatherImpact && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setStatDetailModal(null)}>
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl" onClick={(e) => e.stopPropagation()}>
            
            {/* Weather Alerts Modal */}
            {statDetailModal === 'weather' && (
              <>
                <div className="sticky top-0 bg-gradient-to-r from-orange-600 to-red-600 text-white p-6 rounded-t-2xl">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold">Weather Alerts Details</h2>
                      <p className="text-orange-100 text-sm mt-1">Active weather warnings across cities</p>
                    </div>
                    <button onClick={() => setStatDetailModal(null)} className="p-2 hover:bg-white/20 rounded-lg">
                      <X className="w-6 h-6" />
                    </button>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  <div className="bg-orange-50 border-l-4 border-orange-500 p-4 rounded">
                    <p className="font-bold text-gray-900 text-lg">{weatherImpact.rain_alerts} Active Weather Alerts</p>
                    <p className="text-sm text-gray-600 mt-1">{weatherImpact.critical_zones} classified as critical zones</p>
                  </div>
                  
                  {weatherImpact.city_breakdown?.filter((c: any) => c.rain_alert).map((city: any) => (
                    <div key={city.city} className="bg-white border-l-4 border-orange-400 p-4 rounded-lg shadow-sm">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-bold text-gray-900 text-lg">{city.city}</h3>
                        <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                          city.critical ? 'bg-red-500 text-white' : 'bg-orange-500 text-white'
                        }`}>
                          {city.critical ? 'CRITICAL' : 'ACTIVE ALERT'}
                        </span>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm text-gray-700">
                          🌧️ <span className="font-semibold">Rain Alert Active</span> - Weather warning detected
                        </p>
                        <p className="text-sm text-gray-600">
                          🌡️ Temperature: <span className="font-semibold">{city.temperature}°C</span>
                        </p>
                        <p className="text-sm text-gray-600">
                          💧 Humidity: <span className="font-semibold">{city.humidity}%</span>
                        </p>
                        <p className="text-sm text-gray-600">
                          🚗 Traffic Impact: <span className="font-semibold">{city.traffic_count} incidents</span>
                        </p>
                      </div>
                    </div>
                  ))}
                  
                  {weatherImpact.city_breakdown?.filter((c: any) => !c.rain_alert).length > 0 && (
                    <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                      <p className="font-bold text-gray-900">✅ Clear Weather Cities</p>
                      <p className="text-sm text-gray-600 mt-2">
                        {weatherImpact.city_breakdown?.filter((c: any) => !c.rain_alert).map((c: any) => c.city).join(', ')}
                      </p>
                    </div>
                  )}
                </div>
              </>
            )}

            {/* Traffic Disruptions Modal */}
            {statDetailModal === 'traffic' && (
              <>
                <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-2xl">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold">Traffic Disruptions Details</h2>
                      <p className="text-blue-100 text-sm mt-1">Road closures and accidents across cities</p>
                    </div>
                    <button onClick={() => setStatDetailModal(null)} className="p-2 hover:bg-white/20 rounded-lg">
                      <X className="w-6 h-6" />
                    </button>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  {weatherImpact.city_breakdown?.sort((a: any, b: any) => b.traffic_count - a.traffic_count).map((city: any) => (
                    <div key={city.city} className={`bg-white border-l-4 p-4 rounded-lg shadow-sm ${
                      city.traffic_count >= 5 ? 'border-red-400' :
                      city.traffic_count >= 3 ? 'border-yellow-400' :
                      'border-green-400'
                    }`}>
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-bold text-gray-900 text-lg">{city.city}</h3>
                        <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                          city.traffic_count >= 5 ? 'bg-red-500 text-white' :
                          city.traffic_count >= 3 ? 'bg-yellow-500 text-gray-900' :
                          'bg-green-500 text-white'
                        }`}>
                          {city.traffic_count} Critical
                        </span>
                      </div>
                      <div className="space-y-2">
                        <div 
                          onClick={() => setExpandedTraffic(expandedTraffic === city.city ? null : city.city)}
                          className="cursor-pointer hover:bg-gray-50 p-2 rounded -m-2"
                        >
                          <p className="text-sm text-gray-700 mb-2">
                            🚗 <span className="font-semibold">
                              {city.traffic_count >= 5 ? 'Severe Disruption' :
                               city.traffic_count >= 3 ? 'Moderate Impact' :
                               city.traffic_count >= 1 ? 'Minor Impact' :
                               'Normal Flow'}
                            </span> - {city.traffic_count} critical incidents
                          </p>
                          <p className="text-xs text-blue-600 font-medium">
                            {expandedTraffic === city.city ? '▼ Hide road details' : '▶ Click to see which roads are affected'}
                          </p>
                        </div>
                        
                        {/* Show actual road closures - only when expanded */}
                        {expandedTraffic === city.city && city.traffic_incidents && city.traffic_incidents.length > 0 && (
                          <div className="bg-gray-50 rounded p-3 space-y-2 mb-2 mt-2">
                            <p className="text-xs font-semibold text-gray-700 mb-2">Road Closures & Critical Incidents:</p>
                            {city.traffic_incidents.map((incident: any, idx: number) => (
                              <div key={idx} className="text-xs border-l-2 border-red-400 pl-2 py-1">
                                <p className="font-semibold text-gray-900">
                                  {incident.road_closed ? '🚧 ROAD CLOSED' : '⚠️ CRITICAL'}: {incident.type}
                                </p>
                                <p className="text-gray-700">{incident.description}</p>
                                {incident.start_time && (
                                  <p className="text-gray-500 text-xs mt-1">Since: {new Date(incident.start_time).toLocaleString()}</p>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                        
                        <p className="text-sm text-gray-600">
                          {city.traffic_count >= 5 ? '⚠️ Multiple major roads affected - Significant delays expected' :
                           city.traffic_count >= 3 ? '⚠️ Key routes impacted - Plan extra travel time' :
                           city.traffic_count >= 1 ? 'Some routes affected - Minor delays possible' :
                           '✅ All major routes clear'}
                        </p>
                        {city.rain_alert && (
                          <p className="text-sm text-orange-600 font-medium mt-2">
                            🌧️ Weather alert + Traffic = Compound impact on emergency response
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            {/* Cities Monitored Modal */}
            {statDetailModal === 'cities' && (
              <>
                <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 rounded-t-2xl">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold">Cities Monitored</h2>
                      <p className="text-purple-100 text-sm mt-1">Hackathon scope - Major Indian cities</p>
                    </div>
                    <button onClick={() => setStatDetailModal(null)} className="p-2 hover:bg-white/20 rounded-lg">
                      <X className="w-6 h-6" />
                    </button>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  <div className="grid grid-cols-1 gap-3">
                    {weatherImpact.city_breakdown?.map((city: any, index: number) => (
                      <div key={city.city} className={`bg-white border-l-4 p-4 rounded-lg shadow-sm ${
                        city.status === 'Critical' ? 'border-red-500' :
                        city.status === 'Alert' ? 'border-orange-500' :
                        city.status === 'Warning' ? 'border-yellow-500' :
                        'border-green-500'
                      }`}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-gray-500 text-sm">#{index + 1}</span>
                            <h3 className="font-bold text-gray-900 text-lg">{city.city}</h3>
                          </div>
                          <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                            city.status === 'Critical' ? 'bg-red-500 text-white' :
                            city.status === 'Alert' ? 'bg-orange-500 text-white' :
                            city.status === 'Warning' ? 'bg-yellow-500 text-gray-900' :
                            'bg-green-500 text-white'
                          }`}>
                            {city.status}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                          <div>🌡️ {city.temperature}°C</div>
                          <div>💧 {city.humidity}%</div>
                          <div>{city.rain_alert ? '🌧️ Rain Alert' : '☀️ Clear'}</div>
                          <div>🚗 {city.traffic_count} incidents</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* Severity Status Modal */}
            {statDetailModal === 'severity' && (
              <>
                <div className={`sticky top-0 text-white p-6 rounded-t-2xl ${
                  weatherImpact.severity_index === 'Critical' ? 'bg-gradient-to-r from-red-600 to-red-700' :
                  weatherImpact.severity_index === 'High' ? 'bg-gradient-to-r from-orange-600 to-orange-700' :
                  weatherImpact.severity_index === 'Medium' ? 'bg-gradient-to-r from-yellow-600 to-yellow-700' :
                  'bg-gradient-to-r from-green-600 to-green-700'
                }`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold">Severity Analysis</h2>
                      <p className="text-white/90 text-sm mt-1">Real-time threat assessment algorithm</p>
                    </div>
                    <button onClick={() => setStatDetailModal(null)} className="p-2 hover:bg-white/20 rounded-lg">
                      <X className="w-6 h-6" />
                    </button>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  <div className={`border-l-4 p-4 rounded ${
                    weatherImpact.severity_index === 'Critical' ? 'bg-red-50 border-red-500' :
                    weatherImpact.severity_index === 'High' ? 'bg-orange-50 border-orange-500' :
                    weatherImpact.severity_index === 'Medium' ? 'bg-yellow-50 border-yellow-500' :
                    'bg-green-50 border-green-500'
                  }`}>
                    <p className="font-bold text-gray-900 text-2xl">{weatherImpact.severity_index} Severity</p>
                    <p className="text-sm text-gray-600 mt-1">
                      Score: {weatherImpact.severity_score}/100 based on multi-factor analysis
                    </p>
                  </div>

                  <div className="bg-white border border-gray-200 p-4 rounded-lg">
                    <h3 className="font-bold text-gray-900 mb-3">Severity Calculation</h3>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Critical Weather Zones</span>
                        <span className="font-bold text-gray-900">+{weatherImpact.critical_zones > 0 ? 40 : 0} pts</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Active Rain Alerts (≥3)</span>
                        <span className="font-bold text-gray-900">+{weatherImpact.rain_alerts >= 3 ? 30 : 0} pts</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Traffic Disruptions (≥5)</span>
                        <span className="font-bold text-gray-900">+{weatherImpact.traffic_disruptions >= 5 ? 20 : 0} pts</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">High Humidity (&gt;70%)</span>
                        <span className="font-bold text-gray-900">+{weatherImpact.humidity > 70 ? 10 : 0} pts</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
                    <h3 className="font-bold text-gray-900 mb-3">City Status Breakdown</h3>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-red-100 p-3 rounded">
                        <p className="text-2xl font-bold text-red-700">
                          {weatherImpact.city_breakdown?.filter((c: any) => c.status === 'Critical').length || 0}
                        </p>
                        <p className="text-xs text-red-600">Critical</p>
                      </div>
                      <div className="bg-orange-100 p-3 rounded">
                        <p className="text-2xl font-bold text-orange-700">
                          {weatherImpact.city_breakdown?.filter((c: any) => c.status === 'Alert').length || 0}
                        </p>
                        <p className="text-xs text-orange-600">Alert</p>
                      </div>
                      <div className="bg-yellow-100 p-3 rounded">
                        <p className="text-2xl font-bold text-yellow-700">
                          {weatherImpact.city_breakdown?.filter((c: any) => c.status === 'Warning').length || 0}
                        </p>
                        <p className="text-xs text-yellow-600">Warning</p>
                      </div>
                      <div className="bg-green-100 p-3 rounded">
                        <p className="text-2xl font-bold text-green-700">
                          {weatherImpact.city_breakdown?.filter((c: any) => c.status === 'Normal').length || 0}
                        </p>
                        <p className="text-xs text-green-600">Normal</p>
                      </div>
                    </div>
                  </div>

                  <div className={`p-4 rounded-lg ${
                    weatherImpact.severity_index === 'Critical' ? 'bg-red-100' :
                    weatherImpact.severity_index === 'High' ? 'bg-orange-100' :
                    weatherImpact.severity_index === 'Medium' ? 'bg-yellow-100' :
                    'bg-green-100'
                  }`}>
                    <p className="font-bold text-gray-900 mb-2">⚡ Recommended Action</p>
                    <p className="text-sm text-gray-700">
                      {weatherImpact.severity_index === 'Critical' ? 
                        'Deploy all emergency response teams immediately. Activate disaster protocols and coordinate with local authorities.' :
                       weatherImpact.severity_index === 'High' ?
                        'Prepare emergency response teams. Increase monitoring frequency. Keep teams on standby for deployment.' :
                       weatherImpact.severity_index === 'Medium' ?
                        'Maintain heightened awareness. Monitor situation closely. Prepare contingency plans.' :
                        'Continue routine monitoring. All systems normal. Maintain readiness protocols.'}
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* City Detail Modal */}
      {selectedCity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedCity(null)}>
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl" onClick={(e) => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">{selectedCity.city}</h2>
                  <p className="text-blue-100 text-sm mt-1">Live Weather & Traffic Analysis</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 text-sm font-bold rounded-full ${
                    selectedCity.status === 'Critical' ? 'bg-red-500 text-white' :
                    selectedCity.status === 'Alert' ? 'bg-orange-500 text-white' :
                    selectedCity.status === 'Warning' ? 'bg-yellow-500 text-gray-900' :
                    'bg-green-500 text-white'
                  }`}>
                    {selectedCity.status}
                  </span>
                  <button 
                    onClick={() => setSelectedCity(null)}
                    className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-4">
              {/* Temperature Analysis */}
              <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-5 border border-orange-200">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center text-2xl">
                    🌡️
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900 text-lg mb-2">Temperature Analysis</h3>
                    <p className="text-3xl font-bold text-orange-600 mb-2">{selectedCity.temperature}°C</p>
                    <p className="text-gray-700">
                      {selectedCity.temperature > 32 ? '⚠️ Very Hot - Stay hydrated and avoid prolonged outdoor exposure' : 
                       selectedCity.temperature > 28 ? 'Hot conditions - Take regular breaks in shade' : 
                       selectedCity.temperature > 20 ? '✅ Moderate temperature - Comfortable conditions' : 
                       'Cool weather - Consider light layers'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Humidity Status */}
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-5 border border-blue-200">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-2xl">
                    💧
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900 text-lg mb-2">Humidity Status</h3>
                    <p className="text-3xl font-bold text-blue-600 mb-2">{selectedCity.humidity}%</p>
                    <p className="text-gray-700">
                      {selectedCity.humidity > 80 ? '⚠️ Very High - Uncomfortable conditions, heat index increased' :
                       selectedCity.humidity > 60 ? 'High humidity - Muggy conditions expected' :
                       selectedCity.humidity > 40 ? '✅ Moderate - Comfortable humidity levels' : 
                       'Low humidity - Dry conditions, stay hydrated'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Weather Conditions */}
              <div className={`rounded-xl p-5 border ${
                selectedCity.rain_alert ? 'bg-gradient-to-br from-yellow-50 to-orange-50 border-orange-200' : 
                'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200'
              }`}>
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                    selectedCity.rain_alert ? 'bg-orange-500' : 'bg-green-500'
                  }`}>
                    {selectedCity.rain_alert ? '🌧️' : '☀️'}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900 text-lg mb-2">Weather Conditions</h3>
                    <p className="text-2xl font-bold text-gray-900 mb-2">
                      {selectedCity.rain_alert ? 'Rain Alert Active' : 'Clear Conditions'}
                    </p>
                    <p className="text-gray-700">
                      {selectedCity.rain_alert ? 
                        '⚠️ Active weather alert detected. Carry umbrella, avoid flood-prone areas, and monitor updates.' : 
                        '✅ No weather alerts. Clear conditions expected. Safe for outdoor activities.'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Traffic Impact */}
              <div className={`rounded-xl p-5 border ${
                selectedCity.traffic_count >= 5 ? 'bg-gradient-to-br from-red-50 to-pink-50 border-red-200' :
                selectedCity.traffic_count >= 3 ? 'bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-200' :
                'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200'
              }`}>
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                    selectedCity.traffic_count >= 5 ? 'bg-red-500' :
                    selectedCity.traffic_count >= 3 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}>
                    🚗
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900 text-lg mb-2">Traffic Impact</h3>
                    <p className="text-3xl font-bold text-gray-900 mb-2">{selectedCity.traffic_count} Incidents</p>
                    <p className="text-gray-700">
                      {selectedCity.traffic_count >= 5 ? '⚠️ Severe traffic disruption - Expect major delays, consider alternate routes' :
                       selectedCity.traffic_count >= 3 ? 'Moderate traffic delays - Plan extra travel time' :
                       selectedCity.traffic_count >= 1 ? 'Minor traffic delays - Normal commute with slight delays' : 
                       '✅ Normal traffic flow - Smooth commute expected'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Status Summary */}
              <div className={`rounded-xl p-5 border-2 ${
                selectedCity.status === 'Critical' ? 'bg-red-50 border-red-500' :
                selectedCity.status === 'Alert' ? 'bg-orange-50 border-orange-500' :
                selectedCity.status === 'Warning' ? 'bg-yellow-50 border-yellow-500' :
                'bg-green-50 border-green-500'
              }`}>
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl">⚡</span>
                  <h3 className="font-bold text-gray-900 text-lg">Emergency Status</h3>
                </div>
                <p className={`text-xl font-bold mb-2 ${
                  selectedCity.status === 'Critical' ? 'text-red-700' :
                  selectedCity.status === 'Alert' ? 'text-orange-700' :
                  selectedCity.status === 'Warning' ? 'text-yellow-700' :
                  'text-green-700'
                }`}>
                  {selectedCity.status}: {
                    selectedCity.status === 'Critical' ? 'Immediate Action Required!' :
                    selectedCity.status === 'Alert' ? 'Monitor Situation Closely' :
                    selectedCity.status === 'Warning' ? 'Stay Informed & Alert' :
                    'All Clear - Normal Operations'
                  }
                </p>
                <p className="text-sm text-gray-600">
                  {selectedCity.status === 'Critical' ? 'Deploy emergency response teams and activate disaster protocols immediately.' :
                   selectedCity.status === 'Alert' ? 'Prepare response teams and keep monitoring live data feeds.' :
                   selectedCity.status === 'Warning' ? 'Keep monitoring the situation and prepare contingency plans.' :
                   'Continue routine monitoring and maintain readiness.'}
                </p>
              </div>

            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
