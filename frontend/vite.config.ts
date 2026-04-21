import react from '@vitejs/plugin-react'
import { copyFileSync, createReadStream, existsSync, mkdirSync, readdirSync, statSync } from 'node:fs'
import { extname, resolve, sep } from 'node:path'
import { defineConfig, type Plugin } from 'vite'

process.env.VITE_APP_VERSION ||= 'local'

const generatedImagesDirs = [
  resolve(process.cwd(), '../generated/images'),
  resolve('/generated/images'),
]

function resolveGeneratedImagesDir() {
  const sourceDir = generatedImagesDirs.find((dir) => existsSync(dir))
  if (!sourceDir) {
    throw new Error('generated/images not found; official brand assets are required')
  }
  return sourceDir
}

function copyDirectory(sourceDir: string, targetDir: string) {
  mkdirSync(targetDir, { recursive: true })
  for (const entry of readdirSync(sourceDir)) {
    const sourcePath = resolve(sourceDir, entry)
    const targetPath = resolve(targetDir, entry)
    if (statSync(sourcePath).isDirectory()) {
      copyDirectory(sourcePath, targetPath)
    } else {
      copyFileSync(sourcePath, targetPath)
    }
  }
}

function contentType(pathname: string) {
  const extension = extname(pathname)
  if (extension === '.svg') return 'image/svg+xml'
  if (extension === '.ico') return 'image/x-icon'
  return 'application/octet-stream'
}

function generatedImagesPlugin(): Plugin {
  return {
    name: 'hb-generated-images',
    configureServer(server) {
      server.middlewares.use('/generated/images', (request, response, next) => {
        try {
          const sourceDir = resolveGeneratedImagesDir()
          const relativePath = decodeURIComponent((request.url ?? '').split('?')[0]).replace(/^\/+/, '')
          const assetPath = resolve(sourceDir, relativePath)
          if (assetPath !== sourceDir && !assetPath.startsWith(sourceDir + sep)) return next()
          if (!existsSync(assetPath) || statSync(assetPath).isDirectory()) return next()
          response.setHeader('Content-Type', contentType(assetPath))
          createReadStream(assetPath).pipe(response)
        } catch (error) {
          next(error as Error)
        }
      })
    },
    closeBundle() {
      const sourceDir = resolveGeneratedImagesDir()
      copyDirectory(sourceDir, resolve(process.cwd(), 'dist/generated/images'))
    },
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), generatedImagesPlugin()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/__tests__/setup.ts',
    exclude: ['**/node_modules/**', '**/dist/**', 'e2e/**'],
  },
})
