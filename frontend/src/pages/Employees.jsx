import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import api from '../api/client'

export default function Employees() {
  const [employees, setEmployees] = useState([])
  const [uploading, setUploading] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    api.get('/api/users/').then((r) => setEmployees(r.data))
  }, [])

  async function handleUpload(e) {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    setMsg('')
    const form = new FormData()
    form.append('file', file)
    try {
      const { data } = await api.post('/api/users/upload-csv', form)
      setMsg(`${data.added} əməkdaş əlavə edildi, ${data.skipped} atlandı`)
      const r = await api.get('/api/users/')
      setEmployees(r.data)
    } catch {
      setMsg('Xəta baş verdi')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Əməkdaşlar</h2>
          <p className="text-gray-500 text-sm mt-1">{employees.length} nəfər qeydiyyatda</p>
        </div>
        <label className="cursor-pointer bg-red-600 hover:bg-red-700 text-white text-sm font-semibold px-4 py-2.5 rounded-lg transition">
          {uploading ? 'Yüklənir...' : 'CSV Yüklə'}
          <input type="file" accept=".csv" className="hidden" onChange={handleUpload} />
        </label>
      </div>

      {msg && (
        <div className="mb-4 bg-green-50 border border-green-200 text-green-700 text-sm px-4 py-3 rounded-lg">
          {msg}
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="text-left px-6 py-3 text-gray-500 font-medium">Ad</th>
              <th className="text-left px-6 py-3 text-gray-500 font-medium">Email</th>
              <th className="text-left px-6 py-3 text-gray-500 font-medium">Departament</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {employees.map((emp) => (
              <tr key={emp.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-medium text-gray-900">{emp.name}</td>
                <td className="px-6 py-4 text-gray-500">{emp.email}</td>
                <td className="px-6 py-4">
                  <span className="bg-indigo-50 text-indigo-700 text-xs font-medium px-2.5 py-1 rounded-full">
                    {emp.department || '—'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  )
}
