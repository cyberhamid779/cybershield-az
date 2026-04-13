import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import Layout from '../components/Layout'
import api from '../api/client'

function StatCard({ label, value, sub, color }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className={`text-3xl font-bold ${color || 'text-gray-900'}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const [users, setUsers] = useState([])
  const [campaigns, setCampaigns] = useState([])

  useEffect(() => {
    api.get('/api/users/').then((r) => setUsers(r.data))
    api.get('/api/campaigns/').then((r) => setCampaigns(r.data))
  }, [])

  const chartData = [
    { name: 'Əməkdaşlar', value: users.length },
    { name: 'Kampaniyalar', value: campaigns.length },
    { name: 'Aktiv', value: campaigns.filter((c) => c.status === 'active').length },
  ]

  return (
    <Layout>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-500 text-sm mt-1">LionSafe — Ümumi Baxış</p>
      </div>

      <div className="grid grid-cols-3 gap-5 mb-8">
        <StatCard label="Əməkdaşlar" value={users.length} sub="qeydiyyatda" />
        <StatCard label="Kampaniyalar" value={campaigns.length} sub="cəmi" />
        <StatCard
          label="Aktiv Kampaniyalar"
          value={campaigns.filter((c) => c.status === 'active').length}
          color="text-red-600"
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-base font-semibold text-gray-800 mb-4">Statistika</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData}>
            <XAxis dataKey="name" tick={{ fontSize: 13 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 13 }} />
            <Tooltip />
            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={i === 2 ? '#dc2626' : '#6366f1'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Layout>
  )
}
