# Performance Metrics Guide

## 📊 How to View Metrics

Now that your `chat_api.py` has full telemetry tracking, you can monitor performance in multiple ways!

### Method 1: Terminal Viewer ⚡ (Recommended)

Open a new terminal and run:
```bash
cd C:\Users\Claudio\Desktop\Apromore\Chatbot
python view_metrics.py
```

This shows:
- ✅ Accuracy Metrics (grounded accuracy, routing accuracy)
- ⚡ Latency Metrics (P50, P95, mean response times)
- 👥 Adoption Metrics (active users, sessions, queries)
- 🎯 Resolution Metrics (session resolution rate)
- 📏 Metric Parity (error rates)
- 🚨 Hallucination & Contradiction Rates

### Method 2: Web Dashboard 🌐 (Visual)

Double-click this file:
```
C:\Users\Claudio\Desktop\Apromore\Chatbot\metrics_dashboard.html
```

Or open in browser:
```
file:///C:/Users/Claudio/Desktop/Apromore/Chatbot/metrics_dashboard.html
```

Features:
- Beautiful visual interface
- Auto-refreshes every 30 seconds
- Color-coded metrics (green/yellow/red)
- Real-time updates

### Method 3: API Endpoint 🔌

Direct API access:
```
http://localhost:5000/api/kpis/today
```

Returns JSON with all metrics. Perfect for:
- Custom dashboards
- Integration with monitoring tools
- Automated reporting

### Method 4: Raw Trace Logs 📝

See detailed request traces:
```bash
python view_metrics.py --raw
```

Shows last 5 requests with full details.

---

## 🔄 After Updating chat_api.py

**RESTART your backend server:**

1. Stop the current backend (Ctrl+C in backend terminal)
2. Restart it:
   ```bash
   cd C:\Users\Claudio\Desktop\Apromore\Chatbot\backend
   python chat_api.py
   ```

You should see:
```
🚀 Starting Task Mining Chat API Server...
System Status: ✅ Ready
Telemetry: ✅ Enabled
Log Directory: C:\Users\Claudio\Desktop\Apromore\Chatbot\logs
Metrics: http://localhost:5000/api/kpis/today
```

---

## 📈 What Gets Tracked

### Automatic Tracking
- **Every request** is logged to `logs/traces-YYYYMMDD.jsonl`
- **Latency** for each API call
- **Dataset used** (Salesforce/Amadeus)
- **Query text** (first 100 characters)
- **Response status** (success/error)
- **Timestamp** for time-series analysis

### Computed Metrics
- **P50 Latency**: Median response time
- **P95 Latency**: 95th percentile (catches slow requests)
- **Success Rate**: Percentage of successful requests
- **Error Rate**: Percentage of failed requests
- **Active Users**: Unique sessions per day
- **Queries per Session**: Average engagement

---

## 💡 Tips

1. **Use the chatbot first** - Metrics need data! Make some queries to see numbers.

2. **Check metrics after each session** - See how performance changes.

3. **Monitor latency** - If P95 > 5000ms, there might be performance issues.

4. **Watch error rates** - High error rates indicate problems.

5. **Track adoption** - See if users are engaging with the system.

---

## 📂 File Locations

- **Trace Logs**: `C:\Users\Claudio\Desktop\Apromore\Chatbot\logs\traces-YYYYMMDD.jsonl`
- **Metrics Viewer**: `C:\Users\Claudio\Desktop\Apromore\Chatbot\view_metrics.py`
- **Web Dashboard**: `C:\Users\Claudio\Desktop\Apromore\Chatbot\metrics_dashboard.html`

---

## 🆘 Troubleshooting

### "No traces for today"
- Make sure you've used the chatbot after restarting the backend
- Check that `logs` directory exists
- Verify telemetry is enabled in the startup message

### Web dashboard shows errors
- Make sure backend is running on port 5000
- Check browser console for CORS errors
- Try refreshing the page

### Metrics not updating
- Restart the backend server
- Clear browser cache
- Check that trace files are being written to `logs/` directory

---

## 🎯 Example Workflow

1. **Start backend**: `cd backend && python chat_api.py`
2. **Start frontend**: `cd frontend && npm start`
3. **Use the chatbot**: Ask questions at http://localhost:3000
4. **View metrics**: `python view_metrics.py`
5. **Analyze**: Check latency, accuracy, adoption
6. **Optimize**: Make improvements based on metrics

---

## 📊 Sample Output

```
============================================================
  📊 TODAY'S PERFORMANCE METRICS
============================================================

📅 Date: 20251001
📝 Total Requests: 25

============================================================
  ✅ ACCURACY METRICS
============================================================
  Grounded Accuracy Rate: 95.00%
  Routing Accuracy: 100.00%
  Hallucination Rate: 0.00%
  Contradiction Rate: 0.00%

============================================================
  ⚡ LATENCY METRICS
============================================================
  P50 (Median): 234.50 ms
  P95: 567.80 ms
  Mean: 289.30 ms

============================================================
  👥 ADOPTION METRICS
============================================================
  Active Users (DAU): 3
  Total Sessions: 5
  Queries per Session: 5.00
  Total Queries: 25
```

Happy monitoring! 🎉

