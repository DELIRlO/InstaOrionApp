import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Download, Instagram, Link, Smartphone, Video, CheckCircle, AlertCircle, Plus } from 'lucide-react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [downloadStatus, setDownloadStatus] = useState(null)
  const [deferredPrompt, setDeferredPrompt] = useState(null)
  const [showInstallPrompt, setShowInstallPrompt] = useState(false)

  useEffect(() => {
    // Registrar service worker
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
          .then((registration) => {
            console.log('SW registered: ', registration);
          })
          .catch((registrationError) => {
            console.log('SW registration failed: ', registrationError);
          });
      });
    }

    // Detectar evento de instalação PWA
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallPrompt(true);
    });
  }, [])

  const handleInstallApp = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        setShowInstallPrompt(false);
      }
      setDeferredPrompt(null);
    }
  }

  const handleDownload = async () => {
    if (!url.trim()) {
      setDownloadStatus({ type: 'error', message: 'Por favor, insira uma URL válida do Instagram.' })
      return
    }

    if (!url.includes('instagram.com')) {
      setDownloadStatus({ type: 'error', message: 'Por favor, insira uma URL válida do Instagram.' })
      return
    }

    setIsLoading(true)
    setDownloadStatus(null)

    try {
      const response = await fetch('/api/instagram/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() })
      })

      const data = await response.json()

      if (data.success) {
        setDownloadStatus({ 
          type: 'success', 
          message: data.message,
          videoUrl: data.video_url,
          title: data.title
        })
      } else {
        setDownloadStatus({ 
          type: 'error', 
          message: data.error || 'Erro ao processar o vídeo.' 
        })
      }
    } catch (error) {
      setDownloadStatus({ 
        type: 'error', 
        message: 'Erro de conexão. Verifique se o servidor está funcionando.' 
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleUrlChange = (e) => {
    setUrl(e.target.value)
    if (downloadStatus) {
      setDownloadStatus(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-2 rounded-xl">
                <Instagram className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                InstaOrionapp
              </h1>
            </div>
            {showInstallPrompt && (
              <Button 
                onClick={handleInstallApp}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
              >
                <Plus className="h-4 w-4 mr-2" />
                Instalar App
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Baixe Vídeos do Instagram
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              Grátis e Fácil
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Baixe vídeos, reels e IGTV do Instagram de forma rápida e gratuita. 
            Sem necessidade de login ou instalação de aplicativos.
          </p>
        </div>

        {/* Download Card */}
        <Card className="mb-8 shadow-xl border-0 bg-white/90 backdrop-blur-sm">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center space-x-2 text-2xl">
              <Download className="h-6 w-6 text-purple-600" />
              <span>Baixar Vídeo</span>
            </CardTitle>
            <CardDescription className="text-lg">
              Cole o link do vídeo do Instagram que você deseja baixar
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-col md:flex-row space-y-3 md:space-y-0 md:space-x-3">
              <div className="flex-1 relative">
                <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  type="url"
                  placeholder="https://www.instagram.com/p/..."
                  value={url}
                  onChange={handleUrlChange}
                  className="pl-10 h-12 text-lg border-2 border-gray-200 focus:border-purple-500 transition-colors"
                />
              </div>
              <Button 
                onClick={handleDownload}
                disabled={isLoading}
                className="h-12 px-8 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold text-lg transition-all duration-200 transform hover:scale-105"
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Baixando...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Download className="h-5 w-5" />
                    <span>Baixar</span>
                  </div>
                )}
              </Button>
            </div>

            {/* Status Message */}
            {downloadStatus && (
              <div className={`p-4 rounded-lg border ${
                downloadStatus.type === 'success' 
                  ? 'bg-green-50 text-green-800 border-green-200' 
                  : 'bg-red-50 text-red-800 border-red-200'
              }`}>
                <div className="flex items-start space-x-2">
                  {downloadStatus.type === 'success' ? (
                    <CheckCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  ) : (
                    <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <p className="font-medium">{downloadStatus.message}</p>
                    {downloadStatus.videoUrl && (
                      <div className="mt-3">
                        <p className="text-sm mb-2">Título: {downloadStatus.title}</p>
                        <a 
                          href={downloadStatus.videoUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
                        >
                          <Download className="h-4 w-4" />
                          <span>Baixar Vídeo</span>
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Card className="text-center p-6 border-0 bg-white/70 backdrop-blur-sm hover:bg-white/90 transition-all duration-200 hover:shadow-lg">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Smartphone className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Compatível com Mobile</h3>
            <p className="text-gray-600">
              Funciona perfeitamente em smartphones, tablets e computadores
            </p>
          </Card>

          <Card className="text-center p-6 border-0 bg-white/70 backdrop-blur-sm hover:bg-white/90 transition-all duration-200 hover:shadow-lg">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Video className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Alta Qualidade</h3>
            <p className="text-gray-600">
              Baixe vídeos na melhor qualidade disponível no Instagram
            </p>
          </Card>

          <Card className="text-center p-6 border-0 bg-white/70 backdrop-blur-sm hover:bg-white/90 transition-all duration-200 hover:shadow-lg">
            <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="h-8 w-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">100% Gratuito</h3>
            <p className="text-gray-600">
              Sem taxas, sem assinaturas, sem limites de download
            </p>
          </Card>
        </div>

        {/* How to Use */}
        <Card className="bg-white/70 backdrop-blur-sm border-0">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Como Usar</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="bg-purple-600 text-white w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-3 font-bold text-lg">
                  1
                </div>
                <h4 className="font-semibold mb-2">Copie o Link</h4>
                <p className="text-gray-600 text-sm">
                  Vá ao Instagram, encontre o vídeo desejado e copie o link
                </p>
              </div>
              <div className="text-center">
                <div className="bg-purple-600 text-white w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-3 font-bold text-lg">
                  2
                </div>
                <h4 className="font-semibold mb-2">Cole Aqui</h4>
                <p className="text-gray-600 text-sm">
                  Cole o link no campo acima e clique em "Baixar"
                </p>
              </div>
              <div className="text-center">
                <div className="bg-purple-600 text-white w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-3 font-bold text-lg">
                  3
                </div>
                <h4 className="font-semibold mb-2">Baixe o Vídeo</h4>
                <p className="text-gray-600 text-sm">
                  O vídeo será baixado automaticamente para seu dispositivo
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-sm border-t border-gray-200 mt-16">
        <div className="container mx-auto px-4 py-8 text-center">
          <p className="text-gray-600">
            © 2025 InstaOrionapp. Ferramenta gratuita para baixar vídeos do Instagram.
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Este serviço não é afiliado ao Instagram ou Meta.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App

