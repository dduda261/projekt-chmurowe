// Autoryzacja (Keycloak + Token) ====================

function parseJwt(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return null;
  }
}

function getUserRolesFromToken() {
  const token = sessionStorage.getItem('access_token');
  if (!token) return [];
  const payload = parseJwt(token);
  return payload?.realm_access?.roles || [];
}

function isAdmin() {
  return getUserRolesFromToken().includes('admin');
}

function getLoggedUserFromToken() {
  const token = sessionStorage.getItem('access_token');
  if (!token) return null;
  const payload = parseJwt(token);
  return payload?.preferred_username || payload?.email || null;
}

async function sha256(plain) {
  const encoder = new TextEncoder();
  const data = encoder.encode(plain);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return new Uint8Array(hash);
}

function base64UrlEncode(array) {
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

async function generatePKCE() {
  const code_verifier = base64UrlEncode(crypto.getRandomValues(new Uint8Array(32)));
  const hashed = await sha256(code_verifier);
  const code_challenge = base64UrlEncode(hashed);
  return { code_verifier, code_challenge };
}

//  API ENDPOINTY ====================

const isLocal = window.location.hostname === 'localhost';
const petAPI = '/pets';
const userAPI = '/users';

//  UI i stan użytkownika ====================

let loggedUser = getLoggedUserFromToken();

const authStatus = document.getElementById('auth-status');
const logoutBtn = document.getElementById('logout-btn');
const loginBtn = document.getElementById('login-btn');
const addPetSection = document.getElementById('add-pet-section');
const adminPanel = document.getElementById('admin-panel');

function updateUI() {
  loggedUser = getLoggedUserFromToken();

  authStatus.textContent = loggedUser
    ? `Zalogowano jako: ${loggedUser}`
    : 'Nie jesteś zalogowany';

  logoutBtn.style.display = loggedUser ? 'inline-block' : 'none';
  addPetSection.style.display = loggedUser ? 'block' : 'none';
  loginBtn.style.display = loggedUser ? 'none' : 'inline-block';
  adminPanel.style.display = isAdmin() ? 'block' : 'none';
}

// Wylogowanie ====================

logoutBtn.addEventListener('click', () => {
  sessionStorage.clear();
  localStorage.clear();

  
  window.location.href = `http://localhost:8081/realms/petdopt/protocol/openid-connect/logout?redirect_uri=http://localhost:8080/`;

  updateUI();
  fetchPets(); 
});

// Logowanie ====================

loginBtn.addEventListener('click', async () => {
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('code_verifier');

  const { code_verifier, code_challenge } = await generatePKCE();
  sessionStorage.setItem('code_verifier', code_verifier);

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: 'petdopt-frontend',
    redirect_uri: window.location.origin + '/callback.html',
    scope: 'openid profile email',
    code_challenge_method: 'S256',
    code_challenge,
  });

  window.location.href = `http://localhost:8081/realms/petdopt/protocol/openid-connect/auth?${params.toString()}`;
});
//  Panel Administratora ====================

document.getElementById('show-users-btn')?.addEventListener('click', async () => {
  const token = sessionStorage.getItem('access_token');
  if (!token) {
    alert('Brak tokena. Zaloguj się ponownie.');
    return;
  }

  try {
    const res = await fetch('http://localhost:5001/admin/users', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.status === 401) {
      alert('Nie masz uprawnień');
      return;
    } else if (!res.ok) {
      throw new Error(`Błąd serwera: ${res.status}`);
    }
    const users = await res.json();

    const list = document.getElementById('user-list');
    list.innerHTML = '';
    users.forEach(({ username, email }) => {
      const li = document.createElement('li');
      li.textContent = `${username} (${email})`;
      list.appendChild(li);
    });
  } catch (error) {
    alert(`Nie udało się pobrać użytkowników: ${error.message}`);
  }
});


//  Obsługa ogłoszeń ====================

async function fetchPets() {
  try {
    const token = sessionStorage.getItem('access_token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    const res = await fetch(petAPI, { headers });
    const pets = await res.json();

    const list = document.getElementById('pet-list');
    list.innerHTML = '';

    pets.forEach(pet => {
      const li = document.createElement('li');
      li.innerHTML = `
        <strong>${pet.name}</strong> (${pet.species})<br/>
        Płeć: ${pet.gender || '-'}, Wiek: ${pet.age || '-'}, Lokalizacja: ${pet.location || '-'}<br/>
        ${pet.description || ''}<br/>
        ${pet.image_url ? `<img src="${pet.image_url}" alt="${pet.name}" />` : ''}
      `;

      if (loggedUser && (loggedUser === pet.username || isAdmin())) {
        const delBtn = document.createElement('button');
        delBtn.textContent = 'Usuń ogłoszenie';
        delBtn.onclick = () => deletePet(pet.id);
        li.appendChild(delBtn);
      }

      list.appendChild(li);
    });
  } catch (err) {
    console.error('Błąd podczas pobierania zwierzaków:', err);
  }
}

async function deletePet(id) {
  try {
    const token = sessionStorage.getItem('access_token');
    const res = await fetch(`${petAPI}/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });

    if (res.ok) {
      alert('Usunięto ogłoszenie');
      fetchPets();
    } else {
      const data = await res.json();
      alert('Błąd: ' + (data.error || 'Nie udało się usunąć'));
    }
  } catch (err) {
    alert('Błąd sieci: ' + err.message);
  }
}

// Drag & Drop ====================

const dropArea = document.getElementById('drop-area');
const imageInput = document.getElementById('image-file');

dropArea?.addEventListener('dragover', e => {
  e.preventDefault();
  dropArea.classList.add('dragover');
});

dropArea?.addEventListener('dragleave', e => {
  e.preventDefault();
  dropArea.classList.remove('dragover');
});

dropArea?.addEventListener('drop', e => {
  e.preventDefault();
  dropArea.classList.remove('dragover');
  imageInput.files = e.dataTransfer.files;
});

//  Dodawanie ogłoszenia ====================

document.addEventListener('DOMContentLoaded', () => {
  updateUI();
  fetchPets();

  const petForm = document.getElementById('pet-form');

  petForm?.addEventListener('submit', async e => {
    e.preventDefault();

    if (!loggedUser) {
      alert('Musisz być zalogowany, aby dodać ogłoszenie.');
      return;
    }

    const formData = new FormData(petForm);
    formData.append('username', loggedUser);

    try {
      const token = sessionStorage.getItem('access_token');
      console.log(token)
      const res = await fetch(petAPI, {
        method: 'POST',
        body: formData,
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        alert('Dodano ogłoszenie!');
        petForm.reset();
        fetchPets();
      } else {
        alert('Błąd dodawania ogłoszenia.');
      }
    } catch (err) {
      alert('Błąd sieci: ' + err.message);
    }
  });
});
