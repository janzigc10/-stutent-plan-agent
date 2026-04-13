import { useEffect } from 'react'
import { Navigate, Route, BrowserRouter as Router, Routes, useLocation } from 'react-router-dom'

import { AppShell } from './components/AppShell'
import { CalendarPage } from './pages/CalendarPage'
import { ChatPage } from './pages/ChatPage'
import { LoginPage } from './pages/LoginPage'
import { MePage } from './pages/MePage'
import { CoursesPage } from './pages/CoursesPage'
import { NotificationsPage } from './pages/NotificationsPage'
import { PreferencesPage } from './pages/PreferencesPage'
import { RegisterPage } from './pages/RegisterPage'
import { useAuthStore } from './stores/authStore'

function ProtectedRoute() {
  const location = useLocation()
  const { bootstrap, isBootstrapping, token, user } = useAuthStore()

  useEffect(() => {
    if (token && !user) {
      void bootstrap()
    }
  }, [bootstrap, token, user])

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  if (isBootstrapping || !user) {
    return <main className="screen-state">正在加载...</main>
  }

  return <AppShell />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/me" element={<MePage />} />
          <Route path="/me/courses" element={<CoursesPage />} />
          <Route path="/me/preferences" element={<PreferencesPage />} />
          <Route path="/me/notifications" element={<NotificationsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </Router>
  )
}

export default App
