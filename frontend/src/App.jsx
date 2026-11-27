import { useEffect, useMemo, useState } from 'react'
import { Link, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { api } from './api'
import './App.css'

const CUSTOMER_ID = 'guest'
const categoryIcons = {
  'Fruits & Vegetables': '🥬',
  'Dairy & Eggs': '🥛',
  'Snacks': '🍿',
  'Beverages': '🥤',
  'Personal Care': '🧴',
  'Household Essentials': '🧹',
  'Bakery': '🍞',
}

function Header({ cartCount }) {
  const [loginOpen, setLoginOpen] = useState(false)
  const [search, setSearch] = useState('')
  const navigate = useNavigate()
  const submitSearch = (event) => {
    event.preventDefault()
    navigate('/?search=' + encodeURIComponent(search))
  }
  return (
    <>
      <header className="header">
        <Link to="/" className="brand"><span className="brand-mark">S</span><span>SnapKart</span></Link>
        <button className="location" type="button"><span>Delivery in <b>12 mins</b></span><strong>Home · New Delhi</strong></button>
        <form className="search" onSubmit={submitSearch}>
          <span>⌕</span><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search for groceries" />
        </form>
        <button className="login" onClick={() => setLoginOpen(true)}>Sign in</button>
        <Link className="cart-button" to="/cart"><span>🛒</span><b>{cartCount}</b></Link>
        <Link className="bell" to="/notifications">🔔</Link>
      </header>
      {loginOpen && (
        <div className="modal-backdrop" onClick={() => setLoginOpen(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setLoginOpen(false)}>×</button>
            <h2>Welcome to SnapKart</h2>
            <p>Enter your mobile number to continue</p>
            <input placeholder="+91 98765 43210" />
            <button className="primary full" onClick={() => setLoginOpen(false)}>Continue</button>
          </div>
        </div>
      )}
    </>
  )
}

function ProductCard({ product, onAdd }) {
  return (
    <article className="product-card">
      <div className="product-image-wrap">
        {product.discount >= 12 && <span className="discount-badge">{product.discount}% OFF</span>}
        <img src={product.image} alt={product.name} onError={e => { e.currentTarget.style.display='none' }} />
      </div>
      <div className="product-details">
        <span className="delivery-tag">10 MINS</span>
        <h3>{product.name}</h3>
        <p>{product.quantity}</p>
        <div className="price-row">
          <div><strong>₹{product.sellingPrice}</strong>{product.mrp > product.sellingPrice && <del>₹{product.mrp}</del>}</div>
          <button onClick={() => onAdd(product)}>ADD</button>
        </div>
      </div>
    </article>
  )
}

function Home({ onAdd }) {
  const [products, setProducts] = useState([])
  const [category, setCategory] = useState('All')
  const location = useLocation()
  const search = new URLSearchParams(location.search).get('search') || ''

  useEffect(() => {
    api.get('/api/v1/catalog/products', { params: { category, search } })
      .then(res => setProducts(res.data))
      .catch(() => setProducts([]))
  }, [category, search])

  const categories = ['All','Fruits & Vegetables','Dairy & Eggs','Snacks','Beverages','Personal Care','Household Essentials','Bakery']
  return (
    <main>
      <section className="hero-banner">
        <div><span className="eyebrow">SAVED DAILY</span><h1>Fresh groceries<br />in <em>12 minutes</em></h1><p>Freshness you can taste. Prices you'll love.</p><button onClick={() => document.getElementById('products')?.scrollIntoView({behavior:'smooth'})}>Shop now</button></div>
        <div className="hero-art"><span>🥦</span><span>🥛</span><span>🍎</span><span>🥖</span></div>
      </section>
      <section className="categories">
        <h2>Shop by category</h2>
        <div className="category-row">
          {categories.map(cat => <button key={cat} className={category === cat ? 'active' : ''} onClick={() => setCategory(cat)}>
            <span>{cat === 'All' ? '🛍️' : categoryIcons[cat]}</span><b>{cat}</b>
          </button>)}
        </div>
      </section>
      <section className="product-section" id="products">
        <div className="section-heading"><h2>{search ? `Results for "${search}"` : category === 'All' ? 'Best sellers' : category}</h2><span>Fresh picks for you</span></div>
        {products.length ? <div className="product-grid">{products.map(p => <ProductCard key={p.id} product={p} onAdd={onAdd}/>)}</div> : <div className="empty-state">No products available. Make sure the backend services are running.</div>}
      </section>
    </main>
  )
}

function Cart({ cart, setCart }) {
  const navigate = useNavigate()
  const update = async (item, quantity) => {
    const res = await api.patch(`/api/v1/cart/items/${item.id}`, null, { params: { quantity } })
    setCart(res.data)
  }
  const remove = async (item) => {
    const res = await api.delete(`/api/v1/cart/items/${item.id}`)
    setCart(res.data)
  }
  return (
    <main className="page">
      <h1>Your cart</h1>
      {cart.items?.length ? (
        <div className="cart-layout">
          <div className="cart-items">
            {cart.items.map(item => <article className="cart-item" key={item.id}>
              <img src={item.image} alt={item.name} />
              <div className="cart-item-info"><h3>{item.name}</h3><p>₹{item.price}</p></div>
              <div className="quantity"><button onClick={() => update(item,item.quantity-1)}>−</button><span>{item.quantity}</span><button onClick={() => update(item,item.quantity+1)}>+</button></div>
              <button className="remove" onClick={() => remove(item)}>Remove</button>
            </article>)}
          </div>
          <aside className="summary">
            <h2>Bill details</h2>
            <div><span>Subtotal</span><b>₹{cart.subtotal}</b></div>
            <div><span>Delivery fee</span><b>{cart.delivery ? `₹${cart.delivery}` : 'FREE'}</b></div>
            {cart.subtotal < 499 && <p className="saving">Add ₹{499-cart.subtotal} more for free delivery</p>}
            <div className="total"><span>To pay</span><b>₹{cart.total}</b></div>
            <button className="primary full" onClick={() => navigate('/checkout')}>Proceed to checkout</button>
          </aside>
        </div>
      ) : <div className="empty-state"><span>🛒</span><h2>Your cart is empty</h2><Link className="primary" to="/">Start shopping</Link></div>}
    </main>
  )
}

function Checkout({ cart, setCart }) {
  const [address,setAddress] = useState('Flat 204, Green Heights, New Delhi')
  const [payment,setPayment] = useState('UPI')
  const [placed,setPlaced] = useState(null)
  const navigate = useNavigate()
  const placeOrder = async () => {
    const res = await api.post('/api/v1/orders',{
      customerId:CUSTOMER_ID,address,items:cart.items,subtotal:cart.subtotal,delivery:cart.delivery,total:cart.total,paymentMethod:payment
    })
    await api.delete('/api/v1/cart',{params:{customerId:CUSTOMER_ID}})
    setCart({items:[],subtotal:0,delivery:0,total:0})
    setPlaced(res.data)
  }
  if (placed) return <main className="page success-page"><div className="success-icon">✓</div><h1>Order placed!</h1><p>Your order <b>{placed.id}</b> is confirmed.</p><button className="primary" onClick={() => navigate('/orders')}>Track order</button></main>
  return (
    <main className="page">
      <h1>Checkout</h1>
      <div className="checkout-layout">
        <section className="checkout-card"><h2>Delivery address</h2><textarea value={address} onChange={e=>setAddress(e.target.value)} /><h2>Payment method</h2>
          {['UPI','Debit/Credit Card','Cash on Delivery'].map(method => <label className="payment-option" key={method}><input type="radio" checked={payment===method} onChange={()=>setPayment(method)} /><span>{method}</span></label>)}
        </section>
        <aside className="summary"><h2>Order summary</h2>{cart.items?.map(i=><div key={i.id}><span>{i.name} × {i.quantity}</span><b>₹{i.price*i.quantity}</b></div>)}<div className="total"><span>To pay</span><b>₹{cart.total}</b></div><button className="primary full" disabled={!cart.items?.length || !address} onClick={placeOrder}>Place order</button></aside>
      </div>
    </main>
  )
}

function Orders() {
  const [orders,setOrders] = useState([])
  useEffect(() => { api.get('/api/v1/orders',{params:{customerId:CUSTOMER_ID}}).then(r=>setOrders(r.data)).catch(()=>setOrders([])) },[])
  const timeline = ['Order Placed','Confirmed','Packed','Out for Delivery','Delivered']
  const cancel = async (id) => { await api.post(`/api/v1/orders/${id}/cancel`); setOrders(prev=>prev.map(o=>o.id===id?{...o,status:'Cancelled'}:o)) }
  return <main className="page"><h1>My orders</h1>{orders.length ? orders.map(order=><article className="order-card" key={order.id}>
    <div className="order-head"><div><b>{order.id}</b><span>{order.createdAt}</span></div><strong>₹{order.total}</strong></div>
    <div className="order-items">{order.items.map((item,i)=><span key={i}>{item.name} × {item.quantity}</span>)}</div>
    {order.status !== 'Cancelled' ? <div className="timeline">{timeline.map((step,i)=><div key={step} className={timeline.indexOf(order.status)>=i?'done':''}><i>{timeline.indexOf(order.status)>=i?'✓':''}</i><span>{step}</span></div>)}</div> : <div className="cancelled-banner">Order cancelled</div>}
    <div className="order-footer"><span>{order.paymentMethod} · {order.paymentStatus}</span>{!['Cancelled','Out for Delivery','Delivered'].includes(order.status)&&<button onClick={()=>cancel(order.id)}>Cancel order</button>}</div>
  </article>) : <div className="empty-state"><h2>No orders yet</h2><Link className="primary" to="/">Start shopping</Link></div>}</main>
}

function Notifications() {
  const [items,setItems] = useState([])
  useEffect(()=>{api.get('/api/v1/notifications',{params:{customerId:CUSTOMER_ID}}).then(r=>setItems(r.data)).catch(()=>setItems([]))},[])
  return <main className="page"><h1>Notifications</h1>{items.length ? items.map(n=><article className="notification" key={n.id}><span>{n.type.includes('cancel')?'⚠️':'📦'}</span><div><h3>{n.title}</h3><p>{n.message}</p><small>{n.createdAt}</small></div></article>) : <div className="empty-state"><h2>You're all caught up</h2><p>Order updates will appear here.</p></div>}</main>
}

function Chatbot({ onAdd }) {
  const [open,setOpen] = useState(false)
  const [input,setInput] = useState('')
  const [loading,setLoading] = useState(false)
  const [messages,setMessages] = useState([{role:'assistant',text:"Hi! Welcome to SnapKart. I'm your AI shopping assistant. I can help you discover products, track orders and answer support questions."}])
  const send = async (text) => {
    const message = text || input
    if (!message.trim()) return
    setMessages(m=>[...m,{role:'user',text:message}])
    setInput('')
    setLoading(true)
    try {
      const res = await api.post('/api/v1/ai/chat',{message,customerId:CUSTOMER_ID})
      setMessages(m=>[...m,{role:'assistant',text:res.data.reply,products:res.data.products||[],provider:res.data.provider}])
    } catch {
      setMessages(m=>[...m,{role:'assistant',text:'I’m having trouble reaching support right now. The shopping app is still available.'}])
    } finally { setLoading(false) }
  }
  return <>
    {open && <section className="chat-window">
      <header><div><span className="ai-avatar">✦</span><div><b>SnapKart AI</b><small>Usually replies instantly</small></div></div><button onClick={()=>setOpen(false)}>×</button></header>
      <div className="chat-messages">{messages.map((m,i)=><div key={i} className={`message ${m.role}`}>{m.text}{m.provider&&<small className="provider-label">{m.provider==='gemini'?'Gemini':'Local fallback'}</small>}{m.products?.length>0&&<div className="chat-products">{m.products.slice(0,3).map(p=><div key={p.id}><img src={p.image}/><span>{p.name}</span><b>₹{p.sellingPrice}</b><button onClick={()=>onAdd(p)}>ADD</button></div>)}</div>}</div>)}{loading&&<div className="message assistant typing"><i/><i/><i/></div>}</div>
      {!messages.some(m=>m.role==='user')&&<div className="suggestions">{['Suggest healthy snacks under ₹200','Where is my order?','What payment methods are available?'].map(s=><button key={s} onClick={()=>send(s)}>{s}</button>)}</div>}
      <form className="chat-input" onSubmit={e=>{e.preventDefault();send()}}><input value={input} onChange={e=>setInput(e.target.value)} placeholder="Ask SnapKart AI..." /><button>➤</button></form>
    </section>}
    <button className="chat-fab" onClick={()=>setOpen(v=>!v)} aria-label="Open SnapKart AI">{open?'×':'✦'}<span>{open?'':'Ask AI'}</span></button>
  </>
}

function App() {
  const [cart,setCart] = useState({items:[],subtotal:0,delivery:0,total:0})
  useEffect(() => {
    api.get('/api/v1/cart',{params:{customerId:CUSTOMER_ID}})
      .then(r=>setCart(r.data))
      .catch(()=>{})
  },[])
  const addToCart = async (product) => {
    try {
      const res = await api.post('/api/v1/cart/items',{customerId:CUSTOMER_ID,productId:product.id,name:product.name,image:product.image,price:product.sellingPrice,quantity:1})
      setCart(res.data)
    } catch {}
  }
  const cartCount = useMemo(()=>cart.items?.reduce((sum,item)=>sum+item.quantity,0)||0,[cart])
  return <>
    <Header cartCount={cartCount}/>
    <Routes>
      <Route path="/" element={<Home onAdd={addToCart}/>} />
      <Route path="/cart" element={<Cart cart={cart} setCart={setCart}/>} />
      <Route path="/checkout" element={<Checkout cart={cart} setCart={setCart}/>} />
      <Route path="/orders" element={<Orders/>} />
      <Route path="/notifications" element={<Notifications/>} />
    </Routes>
    <Chatbot onAdd={addToCart}/>
  </>
}

export default App
