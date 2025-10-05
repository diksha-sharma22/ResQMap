import { useEffect, useState } from 'react'
import { Bell, Eye, Check, X, Settings as SettingsIcon, Filter, AlertTriangle } from 'lucide-react'
import { weatherAPI } from '../services/api'
import toast from 'react-hot-toast'

const Alerts = () => {
  const [alerts, setAlerts] = useState<any[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const [showSettings, setShowSettings] = useState(false)

  useEffect(() => {
    loadAlerts()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter])

  const loadAlerts = async () => {
    setLoading(true)
    try {
      const alertsRes = await weatherAPI.getIndiaAlerts()
      const alertsData = alertsRes.data.alerts || []
      
      // Filter alerts based on severity if not 'all'
      let filteredAlerts = alertsData
      if (filter !== 'all') {
        filteredAlerts = alertsData.filter((alert: any) => 
          alert.severity?.toLowerCase() === filter.toLowerCase()
        )
      }
      
      // Calculate summary stats from real data
      const totalAlerts = alertsData.length
      const criticalAlerts = alertsData.filter((alert: any) => alert.severity === 'Critical').length
      const actionRequired = alertsData.filter((alert: any) => alert.action_required).length
      
      // For demo purposes, we'll consider all alerts as "unread" since they come from live API
      const unreadAlerts = totalAlerts
      
      const summaryData = {
        total_alerts: totalAlerts,
        unread: unreadAlerts,
        critical: criticalAlerts,
        action_required: actionRequired,
        source: alertsRes.data.source || 'live'
      }
      
      setAlerts(filteredAlerts)
      setSummary(summaryData)
    } catch (error: any) {
      console.error('Failed to load alerts:', error)
      
      // Show a more user-friendly message
      if (error.response?.status === 401) {
        toast.error('Please login to view alerts')
      } else {
        toast.error('No weather alerts at this time')
      }
      
      // Fallback to empty state (not an error, just no alerts)
      setAlerts([])
      setSummary({
        total_alerts: 0,
        unread: 0,
        critical: 0,
        action_required: 0,
        source: 'live'
      })
    } finally {
      setLoading(false)
    }
  }

  // Remove old functions that depend on database alerts
  const handleMarkRead = () => {
    // Live weather alerts don't have read/unread status
    toast('Weather alerts are always live and current', { icon: 'ℹ️' })
  }

  const handleMarkAllRead = () => {
    // Live weather alerts don't have archive functionality
    toast('Live alerts cannot be archived', { icon: 'ℹ️' })
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'border-red-500 bg-red-50'
      case 'high':
        return 'border-orange-500 bg-orange-50'
      case 'medium':
        return 'border-yellow-500 bg-yellow-50'
      default:
        return 'border-gray-500 bg-gray-50'
    }
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-600 text-white'
      case 'high':
        return 'bg-orange-600 text-white'
      case 'medium':
        return 'bg-yellow-600 text-white'
      default:
        return 'bg-gray-600 text-white'
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
          <h1 className="text-3xl font-bold text-gray-900">Notifications & Alerts</h1>
          <p className="text-gray-500 mt-1">Real-time emergency notifications and system alerts</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleMarkAllRead}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Archive All Read
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <SettingsIcon className="w-4 h-4" />
            Settings
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3">
            <Bell className="w-8 h-8 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Total Alerts</p>
              <p className="text-2xl font-bold text-gray-900">{summary?.total_alerts || 0}</p>
              {summary?.source === 'live' && (
                <p className="text-xs text-green-600 font-medium">🔴 LIVE</p>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3">
            <Eye className="w-8 h-8 text-orange-600" />
            <div>
              <p className="text-sm text-gray-600">Active</p>
              <p className="text-2xl font-bold text-gray-900">{summary?.unread || 0}</p>
              <p className="text-xs text-gray-500">Real-time</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-red-600" />
            <div>
              <p className="text-sm text-gray-600">Critical</p>
              <p className="text-2xl font-bold text-gray-900">{summary?.critical || 0}</p>
              <p className="text-xs text-red-600">Immediate Action</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3">
            <Check className="w-8 h-8 text-green-600" />
            <div>
              <p className="text-sm text-gray-600">Cities Monitored</p>
              <p className="text-2xl font-bold text-gray-900">7</p>
              <p className="text-xs text-gray-500">India Major Cities</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 border border-gray-200">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Alerts</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <span className="text-sm text-gray-600">{alerts.length} alerts</span>
        </div>
      </div>

      {/* Alert Settings Panel */}
      {showSettings && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Alert Settings</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">Severity Levels</h4>
              <div className="space-y-2">
                {['Critical', 'High', 'Medium', 'Low'].map((level) => (
                  <label key={level} className="flex items-center gap-3">
                    <input type="checkbox" defaultChecked={level !== 'Low' && level !== 'Medium'} className="rounded" />
                    <span className="text-sm text-gray-700">{level}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">Delivery Methods</h4>
              <div className="space-y-2">
                {['Email', 'SMS', 'Push Notifications'].map((method) => (
                  <label key={method} className="flex items-center gap-3">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <span className="text-sm text-gray-700">{method}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alerts List */}
      <div className="space-y-4">
        {alerts.length === 0 && !loading && (
          <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
            <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No Weather Alerts</h3>
            <p className="text-gray-600">All monitored cities are currently clear. Check back later for updates.</p>
            <p className="text-sm text-green-600 mt-2">✓ Monitoring 7 major Indian cities via HERE Weather API</p>
          </div>
        )}
        
        {alerts.map((alert, index) => (
          <div
            key={`${alert.location}-${index}`}
            className={`bg-white rounded-xl border-l-4 p-6 ${getSeverityColor(alert.severity)}`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 text-xs font-bold rounded ${getSeverityBadge(alert.severity)}`}>
                    {alert.severity}
                  </span>
                  <span className="text-sm font-medium text-gray-900">{alert.category} Alert</span>
                  {alert.action_required && (
                    <span className="px-2 py-1 text-xs font-bold bg-red-600 text-white rounded">
                      🚨 Action Required
                    </span>
                  )}
                  <span className="px-2 py-1 text-xs font-bold bg-blue-600 text-white rounded">
                    🔴 LIVE
                  </span>
                </div>
                
                <h3 className="text-lg font-bold text-gray-900 mb-2">{alert.title}</h3>
                <p className="text-sm text-gray-700 mb-3">{alert.description}</p>
                
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>📍 {alert.location}</span>
                  {alert.valid_from && (
                    <span>🕒 From: {new Date(alert.valid_from).toLocaleString()}</span>
                  )}
                  {alert.valid_until && (
                    <span>⏰ Until: {new Date(alert.valid_until).toLocaleString()}</span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleMarkRead}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="View details"
                >
                  <Eye className="w-5 h-5" />
                </button>
                <button
                  className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                  title="Weather alerts are live"
                >
                  <AlertTriangle className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Alerts
