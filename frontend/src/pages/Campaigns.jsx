import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import api from '../api/client'

const STATUS_LABEL = {
  draft: { label: 'Qaralama', cls: 'bg-gray-100 text-gray-600' },
  active: { label: 'Aktiv', cls: 'bg-green-100 text-green-700' },
  completed: { label: 'Tamamlandı', cls: 'bg-blue-100 text-blue-700' },
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([])
  const [name, setName] = useState('')
  const [templateId, setTemplateId] = useState('')
  const [creating, setCreating] = useState(false)
  const [launching, setLaunching] = useState(null)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    api.get('/api/campaigns/').then((r) => setCampaigns(r.data))
  }, [])

  async function createCampaign(e) {
    e.preventDefault()
    if (!name || !templateId) return
    setCreating(true)
    try {
      const { data } = await api.post('/api/campaigns/', { name, template_id: Number(templateId) })
      setCampaigns((prev) => [...prev, data])
      setName('')
      setTemplateId('')
      setMsg('Kampaniya yaradıldı')
    } catch {
      setMsg('Xəta baş verdi')
    } finally {
      setCreating(false)
    }
  }

  async function launch(id) {
    setLaunching(id)
    try {
      const { data } = await api.post(`/api/campaigns/${id}/launch`)
      setMsg(`Kampaniya başladıldı — ${data.sent} email göndərildi`)
      const r = await api.get('/api/campaigns/')
      setCampaigns(r.data)
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Xəta baş verdi')
    } finally {
      setLaunching(null)
    }
  }

  return (
    <Layout>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Kampaniyalar</h2>
        <p className="text-gray-500 text-sm mt-1">Phishing simulasiyaları</p>
      </div>

      {/* Yeni kampaniya */}
      <form onSubmit={createCampaign} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <h3 className="text-base font-semibold text-gray-800 mb-4">Yeni Kampaniya</h3>
        <div className="flex gap-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Kampaniya adı"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
          />
          <input
            value={templateId}
            onChange={(e) => setTemplateId(e.target.value)}
            placeholder="Şablon ID (1-5)"
            type="number"
            min="1"
            className="w-36 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
          />
          <button
            type="submit"
            disabled={creating}
            className="bg-red-600 hover:bg-red-700 text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition disabled:opacity-50"
          >
            {creating ? 'Yaradılır...' : 'Yarat'}
          </button>
        </div>
      </form>

      {msg && (
        <div className="mb-4 bg-blue-50 border border-blue-200 text-blue-700 text-sm px-4 py-3 rounded-lg">
          {msg}
        </div>
      )}

      {/* Kampaniya siyahısı */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="text-left px-6 py-3 text-gray-500 font-medium">Ad</th>
              <th className="text-left px-6 py-3 text-gray-500 font-medium">Status</th>
              <th className="text-left px-6 py-3 text-gray-500 font-medium">Əməliyyat</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {campaigns.map((c) => {
              const s = STATUS_LABEL[c.status] || STATUS_LABEL.draft
              return (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">{c.name}</td>
                  <td className="px-6 py-4">
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${s.cls}`}>
                      {s.label}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {c.status === 'draft' && (
                      <button
                        onClick={() => launch(c.id)}
                        disabled={launching === c.id}
                        className="bg-green-600 hover:bg-green-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition disabled:opacity-50"
                      >
                        {launching === c.id ? 'Başladılır...' : 'Başlat'}
                      </button>
                    )}
                  </td>
                </tr>
              )
            })}
            {campaigns.length === 0 && (
              <tr>
                <td colSpan={3} className="px-6 py-8 text-center text-gray-400">
                  Hələ kampaniya yoxdur
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </Layout>
  )
}
