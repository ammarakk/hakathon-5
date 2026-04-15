// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: "nur-scents-api",
      script: "python",
      args: "-m uvicorn production.api.main:app --host 0.0.0.0 --port 8000",
      interpreter: "none",
      cwd: "./",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000,
      env: {
        PYTHONPATH: "."
      },
      error_file: "logs/api-error.log",
      out_file: "logs/api-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss"
    },
    {
      name: "nur-scents-worker",
      script: "python",
      args: "production/workers/message_processor.py",
      interpreter: "none",
      cwd: "./",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: "."
      },
      error_file: "logs/worker-error.log",
      out_file: "logs/worker-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss"
    },
    {
      name: "nur-scents-dashboard",
      script: "npm",
      args: "run dev",
      interpreter: "none",
      cwd: "./web-form",
      watch: false,
      autorestart: true,
      max_restarts: 5,
      env: {
        PORT: 3000,
        NODE_ENV: "development"
      },
      error_file: "logs/dashboard-error.log",
      out_file: "logs/dashboard-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss"
    }
  ]
};
