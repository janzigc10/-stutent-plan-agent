import { Link, useNavigate } from 'react-router-dom'

import { useAuthStore } from '../stores/authStore'

export function MePage() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)

  function signOut() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <main className="page me-page">
      <nav className="me-menu" aria-label="我的菜单">
        <Link to="/me/courses">课表管理</Link>
        <Link to="/me/preferences">偏好设置</Link>
        <Link to="/me/notifications">通知设置</Link>
      </nav>
      <button className="primary-button" type="button" onClick={signOut}>
        退出登录
      </button>
    </main>
  )
}
