# Optimization Recommendations for Local Deployment

This document provides optimization strategies to enhance the performance and efficiency of Luna AI when running locally.

## 1. Model Optimization

### Use Local LLM Models
**Current**: Supports cloud-based LLMs (GPT, Claude, Gemini, etc.)  
**Optimization**: Use local models for reduced latency and cost
- **Recommended Models**:
  - `Ollama` with models like Llama 3.2, Mistral, or Qwen (already supported)
  - `text-generation-webui` for larger models with GPU acceleration
  - `koboldcpp` for CPU-optimized inference
  - `LLM_TPU` for specialized hardware

**Benefits**:
- Zero API costs
- Sub-second response times
- Complete privacy (no data leaves your machine)
- No internet dependency

### Quantized Models
**Recommendation**: Use quantized models (4-bit or 8-bit) to reduce memory usage
- **Example**: Llama-3.2-8B-Instruct-Q4_K_M (only ~5GB RAM instead of 16GB)
- **Tools**: Use `llama.cpp` format models with Ollama or koboldcpp
- **Performance**: 2-3x faster inference on CPU with minimal quality loss

## 2. Text-to-Speech (TTS) Optimization

### Local TTS Engines
**Current**: Supports 15+ TTS services (many cloud-based)  
**Optimization**: Prioritize local engines

**Recommended Local TTS**:
1. **Edge-TTS** (fastest, already supported)
   - Offline after initial download
   - Excellent quality
   - Multiple languages
   
2. **VITS-Fast** (already supported)
   - GPU-accelerated for real-time synthesis
   - Custom voice training capability
   
3. **GPT_SoVITS** (already supported)
   - Voice cloning with minimal samples
   - Great for personalized voices
   
4. **ChatTTS** (already supported)
   - Lightweight, fast inference
   - Good for conversational speech

**Performance Tips**:
- Preload TTS models at startup to avoid cold-start delays
- Use GPU for VITS/GPT-SoVITS (5-10x faster than CPU)
- Consider voice caching for common responses

## 3. Live2D/Avatar Rendering Optimization

### GPU Acceleration
**Current**: Live2D rendering via HTML5 canvas  
**Optimization**: Ensure GPU acceleration is enabled

**Browser Settings**:
- Use Chrome/Edge with hardware acceleration enabled
- Resolution: Set Live2D canvas to native resolution (avoid scaling)
- Frame Rate: Lock to 60fps (reduce to 30fps on low-end systems)

**Alternative Renderers**:
- **VTube Studio**: More efficient than browser-based Live2D
- **EasyAIVtuber**: Lightweight alternative with lower resource usage

## 4. Database & Storage Optimization

### SQLite Optimization
**Current**: Uses SQLite for local data storage  
**Optimizations**:

```python
# Add to database initialization
PRAGMA journal_mode=WAL;  # Write-Ahead Logging (faster writes)
PRAGMA synchronous=NORMAL;  # Balance safety and speed
PRAGMA cache_size=-64000;  # 64MB cache
PRAGMA temp_store=MEMORY;  # Use RAM for temp tables
```

### Log Management
**Current**: Logs rotate by size (default 100MB)  
**Optimization**: Add time-based rotation

```json
{
  "webui": {
    "log": {
      "log_level": "WARNING",  // Reduce from INFO
      "max_file_size": "10 MB",  // Smaller files
      "retention_days": 7  // Auto-delete old logs
    }
  }
}
```

## 5. Memory & CPU Optimization

### Python Process Optimization

**Recommended Python Flags**:
```bash
# Run with optimizations
python -O -OO main.py

# For lower memory usage
python -Xfrozen_modules=off main.py
```

**Memory Profiling**:
```bash
# Install memory profiler
pip install memory-profiler

# Profile memory usage
python -m memory_profiler main.py
```

### Multiprocessing
**Current**: Single-threaded for most operations  
**Optimization**: Use process pools for parallel tasks

**Key Areas for Parallelization**:
- Audio synthesis (multiple TTS requests)
- Image generation (Stable Diffusion)
- Chat message processing (if handling multiple platforms)

## 6. Network & Streaming Optimization

### WebSocket Optimization
**Current**: WebSocket for Live2D communication  
**Optimizations**:
- Use message batching (send 10 updates/sec instead of 60)
- Compress WebSocket messages (enable permessage-deflate)
- Local-only binding (127.0.0.1 instead of 0.0.0.0)

### Streaming Platform Optimization
**Recommendation**: Focus on one platform at a time
- Running multiple platform listeners increases CPU/memory usage
- Disable unused platforms in config.json

## 7. Disk I/O Optimization

### Audio File Management
**Current**: Saves all TTS output to `./out/` directory  
**Optimizations**:
- Enable in-memory audio playback (skip file writes)
- Auto-delete old audio files (keep last 100)
- Use RAMdisk for temp audio storage

**Config Change**:
```json
{
  "play_audio": {
    "enable": true,
    "out_path": "/dev/shm/out",  // Linux RAMdisk
    "cache_audio": false,  // Don't save files
    "cleanup_on_exit": true
  }
}
```

## 8. Dependency Optimization

### Reduce Dependencies
**Current**: 100+ dependencies in requirements.txt  
**Optimization**: Create minimal requirement files

```bash
# Create minimal install for local-only usage
pip install -r requirements_minimal.txt
```

**Essential Packages Only**:
- Core: fastapi, uvicorn, nicegui
- LLM: ollama (if using local models)
- TTS: edge-tts or pyttsx3
- Utils: loguru, requests

### Virtual Environment
**Recommendation**: Use `venv` instead of global Python
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 9. Configuration Tuning

### Recommended config.json Changes for Local Optimization

```json
{
  "platform": "talk",  // Local chat mode
  "play_audio": {
    "enable": true,
    "text_split_enable": false,  // Reduce latency
    "interval_num_min": 0,
    "interval_num_max": 0,
    "player": "pygame"  // Faster than external players
  },
  "webui": {
    "log": {
      "log_level": "WARNING"  // Less logging overhead
    }
  },
  "before_prompt": "Respond briefly:",  // Shorter prompts = faster LLM
  "visual_body": "Live2D"  // Most efficient renderer
}
```

## 10. Hardware Recommendations

### Minimum Specs (Local-Only)
- **CPU**: 4-core Intel i5/Ryzen 5 or better
- **RAM**: 8GB (16GB recommended)
- **GPU**: Not required (CPU-only works)
- **Storage**: 10GB free space (20GB with models)

### Recommended Specs (Optimal Performance)
- **CPU**: 8-core Intel i7/Ryzen 7 or better
- **RAM**: 16GB minimum (32GB ideal)
- **GPU**: NVIDIA RTX 3060+ with 8GB+ VRAM (for local LLM + TTS)
- **Storage**: SSD with 50GB+ free space

### GPU Acceleration Benefits
With NVIDIA GPU:
- **Local LLM**: 5-10x faster inference
- **TTS**: 3-5x faster synthesis  
- **Live2D**: Smoother 60fps rendering
- **Stable Diffusion**: Real-time image generation

## 11. Startup Time Optimization

### Lazy Loading
**Modification**: Load models on-demand instead of at startup

```python
# Example: Load LLM only when first message arrives
class LazyLLM:
    def __init__(self):
        self._model = None
    
    @property
    def model(self):
        if self._model is None:
            self._model = load_llm()
        return self._model
```

### Precompiled Bytecode
```bash
# Compile Python files to bytecode
python -m compileall .
```

## 12. Monitoring & Profiling

### Performance Monitoring
**Tools**:
```bash
# CPU/Memory monitoring
pip install psutil
python -m psutil  # System stats

# Profile code execution
python -m cProfile -o profile.stats main.py
python -m pstats profile.stats
```

### Real-time Monitoring
Add to webui.py:
- CPU usage graph
- Memory usage graph  
- Response time metrics
- TTS synthesis time
- LLM inference time

## 13. Docker Optimization (Optional)

### Lightweight Container
```dockerfile
# Use slim Python image
FROM python:3.10-slim

# Multi-stage build to reduce size
FROM python:3.10 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app

# Run optimized
CMD ["python", "-O", "main.py"]
```

### Resource Limits
```yaml
# docker-compose.yml
services:
  luna-ai:
    image: luna-ai
    mem_limit: 4g
    cpus: 2
```

## Summary: Quick Wins for Local Performance

1. ✅ **Use Ollama** with Llama-3.2-8B-Q4 (fast, free, local LLM)
2. ✅ **Enable Edge-TTS** (fast, offline TTS)
3. ✅ **Set log_level to WARNING** (reduce I/O overhead)
4. ✅ **Use Live2D** (most efficient avatar)
5. ✅ **Disable unused platforms** (reduce CPU/memory)
6. ✅ **Enable GPU acceleration** (if available)
7. ✅ **Use SSD storage** (faster file I/O)
8. ✅ **Limit audio file caching** (save disk space)
9. ✅ **Run in virtual environment** (clean dependencies)
10. ✅ **Monitor performance** (identify bottlenecks)

## Expected Performance Improvements

With these optimizations on recommended hardware:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Startup Time | 15-30s | 5-10s | 2-3x faster |
| Response Latency | 2-5s | 0.5-1s | 4-5x faster |
| Memory Usage | 4-8GB | 2-4GB | 50% reduction |
| CPU Usage (idle) | 15-25% | 5-10% | 60% reduction |
| Disk I/O | Heavy | Minimal | 80% reduction |

---

**Note**: These optimizations assume local-only deployment. If using cloud services (streaming, cloud LLMs), network latency will be the primary bottleneck.

**Last Updated**: 2026-02-11
