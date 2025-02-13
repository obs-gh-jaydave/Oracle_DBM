## Prerequisites for Running on Apple Silicon

If you're using Apple Silicon, follow these steps:

1. Install Colima:
   ```
   brew install colima
   ```

2. Start Colima with specific architecture and memory settings:
   ```
   colima start --arch x86_64 --memory 4
   ```

3. Build and run Docker containers:
   ```
   docker compose build --no-cache
   docker compose up
   ```

These steps ensure compatibility and proper setup for running the application on Apple Silicon machines.