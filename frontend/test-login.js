async function checkLogin(username, password) {
  try {
    const res = await fetch('https://qa.rvaldiviase.me/api/user/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usuNom: username, password: password })
    });
    const text = await res.text();
    console.log(`[${username}] Status: ${res.status} - Response: ${text}`);
  } catch (e) {
    console.error(`[${username}] Error:`, e.message);
  }
}

async function run() {
  await checkLogin('vendedor1', 'Admin123!');
  await checkLogin('gerente1', 'Admin123!');
  await checkLogin('cajero1', 'Admin123!');
  await checkLogin('admin', 'admin123');
}

run();
