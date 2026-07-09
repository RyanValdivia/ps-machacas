async function checkCashes() {
  try {
    const res = await fetch('https://qa.rvaldiviase.me/api/user/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usuNom: 'admin', password: 'admin123' })
    });
    const data = await res.json();
    const token = data.access;

    const cashesRes = await fetch('https://qa.rvaldiviase.me/api/cash/cash/', {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const cashes = await cashesRes.text();
    console.log(`Cashes: ${cashes}`);
  } catch (e) {
    console.error(`Error:`, e.message);
  }
}
checkCashes();
