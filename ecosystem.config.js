module.exports = {
  apps: [{
    name: 'gomgom-ai',
    script: 'uvicorn',
    interpreter: '/home/ubuntu/gom/venv/bin/python',
    args: 'app.main:app --host 0.0.0.0 --port 8000',
    cwd: '/home/ubuntu/gom',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '/home/ubuntu/gom'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: '/home/ubuntu/.pm2/logs/gomgom-ai-error.log',
    out_file: '/home/ubuntu/.pm2/logs/gomgom-ai-out.log',
    log_file: '/home/ubuntu/.pm2/logs/gomgom-ai-combined.log',
    time: true
  }]
}; 