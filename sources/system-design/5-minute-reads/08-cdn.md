# 🟡 #8 — CDN: Content Delivery Networks (5-min read)

## 🎯 TL;DR
**A CDN is hundreds of servers spread around the world that cache your static content close to users. It's the cheapest, easiest, biggest performance win in web development.**

---

## 📖 Plain English

Your web server is in **Virginia**. A user in **Tokyo** loads your site. The packets must cross the Pacific (≈150ms each way). Multiply by 50 assets (CSS, JS, images) and the page is slow.

A **CDN** (Cloudflare, CloudFront, Fastly, Akamai) has a server in Tokyo that caches your assets. The Tokyo user fetches at <20ms. Same site. Same code. **10x faster.**

```
Without CDN:  Tokyo user ────────────────► Virginia server (150ms RTT)
With CDN:     Tokyo user → Tokyo edge cache (15ms)
                                       ↓
                                cache hit, served instantly
```

---

## 🔑 What CDNs Cache (and don't)

✅ **Great fit:**
- Images, videos, fonts, CSS, JS bundles
- API responses with `Cache-Control: max-age` headers
- HTML pages for static sites
- Software downloads (npm, pip, Docker images)
- Live video segments (HLS chunks)

❌ **Bad fit (don't cache):**
- Personalized content (logged-in user dashboards)
- Real-time data (live trading prices, chat messages)
- Sensitive data (account details, JWT tokens)
- POST/PUT/DELETE responses

---

## 🌎 Push CDN vs Pull CDN

### Pull CDN (default, easiest)
```
First request:   Tokyo user → Edge (miss) → Origin → Edge (cache) → User
Future requests: Tokyo user → Edge (hit)  → User
```
- You upload to your origin once. CDN fetches lazily on first miss.
- ✅ Simple; auto-cached on demand
- ❌ First request slow ("cold cache")
- **Use for:** Most websites, blogs, e-commerce, SaaS

### Push CDN
```
You explicitly upload to CDN edge nodes via API.
Origin is not involved during requests at all.
```
- ✅ Full control; first request fast
- ❌ More complex (you manage cache invalidation)
- **Use for:** Large infrequently-updated assets (game patches, software releases)

---

## 🔄 Cache Invalidation — The Hard Part

You changed your `style.css`. CDN edges still serve the old one. Now what?

### Strategy 1: TTL (Time-To-Live)
```http
Cache-Control: public, max-age=86400   # cached for 1 day
```
Wait it out. Simple. Fine for stable assets.

### Strategy 2: Cache-busting URLs (the modern way) ★
```html
<link rel="stylesheet" href="/style.css?v=42b3f9c">
<!-- file actually deployed as /style.42b3f9c.css -->
```
- New version → new URL → new cache entry
- Old version is invalidated by being unreferenced
- Used by every modern build tool (webpack, Vite, Next.js)

### Strategy 3: Manual purge / invalidation
- Call CDN API: "purge `/style.css` everywhere"
- Cloudflare: < 30 seconds globally
- AWS CloudFront: ~10 minutes
- ❌ Costs money; rate-limited

**Modern best practice:** Use cache-busting URLs (long TTL + new URLs on change). You'll thank yourself.

---

## 📊 Real-World Performance Wins

| Metric | Without CDN | With CDN |
|---|---|---|
| First Contentful Paint (Tokyo user, US origin) | 1.8s | 0.4s |
| Bandwidth cost | $0.09/GB (origin) | $0.02-0.08/GB (CDN) |
| Origin server load | Full | 1-10% |
| DDoS protection | None | Built-in |

A CDN in front of your service:
- **Faster** for users
- **Cheaper** (cuts origin bandwidth 90%+)
- **More reliable** (origin can be down briefly without users noticing)
- **Safer** (absorbs DDoS, hides origin IP)

---

## 🏗️ How Big CDNs Work

Most CDNs operate **hundreds of POPs** (Points of Presence) globally:
- **Cloudflare:** 300+ cities
- **AWS CloudFront:** 410+ edge locations
- **Akamai:** 4,000+ POPs (yes, four thousand)

Each POP has SSDs full of cached objects. Routing uses **anycast IP**: same IP advertised from every POP; BGP routes the user to the closest one.

**Netflix** has its own CDN — **Open Connect** — with custom hardware in ISPs to stream video from inside the user's ISP network.[^1]

---

## 🚦 Practical Setup

For most apps, this is the entire CDN config:

```nginx
# Your asset path
GET /static/app.42b3f9c.js

# Response headers
Cache-Control: public, max-age=31536000, immutable   # 1 year
ETag: "42b3f9c"
```

That's it. Set it once. Profit forever.

---

## 🔗 Dig Deeper

- 📘 [karanpratapsingh/system-design — CDN section](https://github.com/karanpratapsingh/system-design)
- 📺 [ByteByteGo: How CDN works](https://www.youtube.com/@ByteByteGo)
- 📘 [Netflix Open Connect overview](https://openconnect.netflix.com/)

---

## 📖 Citations

[^1]: `binhnguyennus/awesome-scalability` repo — Netflix Open Connect CDN architecture.

---

← [Back to 5-min reads index](./README.md)
