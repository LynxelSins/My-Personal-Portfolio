# Personal Portfolio 
**For CP352005 Computer Network**

***

นางสาวปภาวรินทร์ นาเมืองรักษ์ 

673380275-5 

Section 01 

Email: Phapawarin.n@kkumail.com 


***
# Final Project — Role

> **วิชา:** Computer Networks (Undergraduate)  
> **ตำแหน่ง:** Network Engineer  
> **โปรเจกต์:** ออกแบบและพัฒนาระบบเครือข่ายภูเขาสูงที่ทนต่อการขาดการเชื่อมต่อ
---
Link to project : https://github.com/Nattha-nan/High-Mountain-Network.git
---

## 👤 งานที่รับผิดชอบ

ในฐานะ Network Engineer ของกลุ่ม รับผิดชอบงานหลัก 5 ด้าน:

1. **ออกแบบ Network Topology** — วางโครงสร้าง 13 nodes, 5 networks, 3 ชั้นตามที่ Architect ออกแบบไว้ สำหรับการสร้างโดย container
2. **Implement DTN (Delay-Tolerant Networking)** — เขียน store-and-forward logic ใน Python
3. **Implement QoS Priority Queue** — จัดลำดับ traffic ตามความสำคัญ
4. **Implement Energy Simulation** — จำลองพฤติกรรมเครือข่ายเมื่อพลังงานต่ำในไฟล์ app.py
5. **สร้าง AI Monitoring Script** — ตรวจจับ anomaly อัตโนมัติ สำหรับ monitoring การทำงานของเครือข่าย

---

##  Network Topology ที่ออกแบบ

### ภาพรวม 3 ชั้น

```
                   Internet Gateway
                          │
          ┌───────────────┼───────────────┐
     Summit Alpha     Summit Beta     Summit Gamma
          │    ╲           │           ╱    │
          │     ╲          │          ╱     │
     Relay North  ╲  Relay Center  ╱   Relay East
          │         ╲      │      ╱         │
    Village A/B    Village B/C    Village C/D
          │                               │
   Sensor Cluster 1           Sensor Cluster 2
```

### เหตุผลที่เลือก Topology นี้

เครือข่ายภูเขาสูงมีปัญหาหลักคือลิงก์ขาดบ่อย จึงออกแบบให้ทุก node มี **อย่างน้อย 2 เส้นทาง** ไปยัง backbone เสมอ ตามหลัก **Graph Theory — 2-connected topology** ซึ่งรับประกันว่าต้องตัดลิงก์พร้อมกันอย่างน้อย 2 เส้น ถึงจะทำให้ node ใด node หนึ่งขาดจากระบบได้

### การแบ่ง Network (IP Planning)

| Network | Subnet | บทบาท |
|---|---|---|
| backbone_net | 172.20.0.0/24 | Summit ↔ Summit |
| access_net_north | 172.21.0.0/24 | ฝั่งเหนือ |
| access_net_east | 172.22.0.0/24 | ฝั่งตะวันออก |
| access_net_south | 172.23.0.0/24 | กลาง |
| sensor_net | 172.24.0.0/24 | IoT เท่านั้น (isolated) |

> `sensor_net` ตั้งเป็น internal เพื่อป้องกัน sensor ออก internet โดยตรง — เป็นการทำ **Network Segmentation** ตามหลัก Security

---

##  โค้ดที่เขียน

### 1. Network Topology — `docker-compose.yml`

กำหนด IP และ network ของทุก node ให้สอดคล้องกับ topology ที่ออกแบบ แต่ละ node อยู่ใน **หลาย network พร้อมกัน** ตามบทบาท เช่น `relay-center` อยู่ใน 4 networks เพื่อเป็นจุดเชื่อมกลาง:

```yaml
relay-center:
  environment:
    - NODE_NAME=relay-center
    - NODE_ROLE=relay
    - NEIGHBORS=summit-alpha,summit-beta,summit-gamma,village-b,village-c
  networks:
    backbone_net:
      ipv4_address: 172.20.0.21
    access_net_north:
      ipv4_address: 172.21.0.21
    access_net_east:
      ipv4_address: 172.22.0.21
    access_net_south:
      ipv4_address: 172.23.0.21
```

---

### 2. DTN Store-and-Forward — `app.py`

หัวใจของระบบคือ `try_deliver()` — ถ้าส่งไม่ได้จะเก็บใน queue แทนที่จะ error:

```python
async def try_deliver(msg: Message):
    target = None
    for n in NEIGHBORS:
        if n.strip() == msg.destination:
            target = n.strip()
            break

    if not target:
        dtn_queue.append(msg.model_dump())
        return {"status": "queued", "reason": "destination not in neighbors"}

    url = f"http://{target}:8000/receive"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(url, json=msg.model_dump())
            result = response.json()
            if result.get("status") == "rejected":
                return {"status": "rejected", "reason": result.get("reason"), "to": target}
        return {"status": "delivered", "to": target}
    except Exception as e:
        dtn_queue.append(msg.model_dump())
        return {"status": "queued", "reason": str(e)}
```

และ `retry_loop()` ที่รันเบื้องหลังทุก 30 วินาที พร้อม QoS sorting:

```python
async def retry_loop():
    priority_order = {"emergency": 0, "telemetry": 1, "normal": 2}
    while True:
        await asyncio.sleep(30)
        sorted_queue = sorted(
            dtn_queue,
            key=lambda m: priority_order.get(m.get("priority", "normal"), 2)
        )
        failed = []
        for msg_dict in sorted_queue:
            msg = Message(**msg_dict)
            url = f"http://{msg.destination}:8000/receive"
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    await client.post(url, json=msg_dict)
                print(f"[QoS] Delivered [{msg.priority}] → {msg.destination}")
            except:
                failed.append(msg_dict)
        dtn_queue.clear()
        dtn_queue.extend(failed)
```

---

### 3. Energy Simulation — `app.py`

จำลองพฤติกรรมเมื่อพลังงานต่ำ — ถ้า energy < 20% จะเข้า low power mode อัตโนมัติ:

```python
@app.post("/energy")
async def set_energy(data: dict):
    global energy_level, low_power_mode
    energy_level = max(0, min(100, data.get("level", 100)))
    if energy_level < 20:
        low_power_mode = True
    elif energy_level >= 50:
        low_power_mode = False

@app.post("/receive")
async def receive_message(msg: Message):
    if low_power_mode and msg.priority in ["normal", "telemetry"]:
        return {"status": "rejected", "reason": "low power mode"}
    message_log.append(msg.model_dump())
    return {"status": "received", "node": NODE_NAME, "message": msg.content}
```

---

### 4. AI Monitoring — `monitor.py`

Script ตรวจสอบสุขภาพเครือข่ายทุก 10 วินาที และแจ้งเตือนเมื่อพบความผิดปกติ:

```python
def detect_anomalies(results: list) -> list:
    anomalies = []
    for r in results:
        if r["status"] == "offline":
            anomalies.append({"severity": "CRITICAL", "issue": "Node offline"})
        if r["queue_size"] >= QUEUE_THRESHOLD:
            anomalies.append({"severity": "WARNING", "issue": "DTN queue ใหญ่ผิดปกติ"})
        emergency_stuck = [m for m in r.get("raw_queue", [])
                          if m.get("priority") == "emergency"]
        if emergency_stuck:
            anomalies.append({"severity": "CRITICAL", "issue": "Emergency ค้างใน queue!"})
    return anomalies
```


---

## 🔗 เชื่อมโยงกับทฤษฎีในวิชา

| สิ่งที่ implement | ทฤษฎีที่อ้างอิง | อธิบาย |
|---|---|---|
| Mesh Topology (≥2 เส้นทาง) | **Graph Theory** | 2-connected graph รับประกัน redundancy |
| DTN Store-and-Forward | **Delay-Tolerant Networking** | Bundle Protocol — ไม่พึ่ง TCP session ต่อเนื่อง |
| Network Segmentation (5 subnets) | **OSI Layer 3** | แยก broadcast domain ตาม function |
| QoS Priority Queue | **Queuing Theory** | Weighted Priority Queuing — emergency ได้ bandwidth ก่อน |
| Energy Mode | **Resilient Network Design** | Graceful Degradation — ล้มได้แต่ยังทำงานบางส่วน |
| AI Monitor | **Network Management** | Anomaly Detection จาก log และ metrics |

---

## 📝 สิ่งที่เรียนรู้

**ด้าน Networking:**
- การออกแบบ topology ให้ทนต่อ single point of failure ต้องคิดจาก Graph Theory จริงๆ ไม่ใช่แค่วาดเส้นให้เยอะ
- Network Segmentation ไม่ได้มีแค่ด้าน security แต่ช่วยควบคุม traffic flow ได้ชัดเจนขึ้น
- DTN เหมาะกับสภาพแวดล้อมที่ TCP ทำงานได้ไม่ดี เพราะ TCP ต้องการ session ต่อเนื่อง

**ด้าน Implementation:**
- Container networking จำลอง physical network ได้ดีมาก แต่มีข้อจำกัดเรื่อง rootless Podman ที่เข้าถึง IP ของ container ตรงๆ จากภายนอกไม่ได้
- การใช้ environment variable แทน hardcode ทำให้ใช้โค้ดชุดเดียวกับทุก node ได้ ลด duplication
- การเลือกใช้ตัว Container ถ้าเป็น Windows ควรที่จะเลือกใช้ Docker มากกว่า Podman ส่วน Linux ใช้ Podman ได้ โดยเฉพาะอย่างยิ่ง กับ Fedora ซึ่งเป็นบริษัทเดียวกันกับที่สร้าง Podman คือ Redhat
- `async/await` ใน Python สำคัญมากสำหรับ network application เพราะ I/O bound task จะไม่บล็อก event loop
