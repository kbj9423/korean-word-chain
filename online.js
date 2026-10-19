// 같이하기: Firestore 방(wordchain-rooms/{방 코드})에 단어를 주고받는다. 같은 Firebase 프로젝트를 다른 게임들과 함께 쓴다.
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.16.0/firebase-app.js";
import { getAuth, signInAnonymously, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/12.16.0/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc, deleteDoc, onSnapshot, runTransaction, serverTimestamp, Timestamp }
  from "https://www.gstatic.com/firebasejs/12.16.0/firebase-firestore.js";

const app = initializeApp({
  apiKey: "AIzaSyDezOLAjvNULnBgCxunb2u1cjqrAIqtQEs",
  authDomain: "arrowgame-e9ac7.firebaseapp.com",
  projectId: "arrowgame-e9ac7",
  storageBucket: "arrowgame-e9ac7.firebasestorage.app",
  messagingSenderId: "1023234573327",
  appId: "1:1023234573327:web:8c11439fdd39dfd3130f7a"
});
const auth = getAuth(app), db = getFirestore(app);
const ROOMS = "wordchain-rooms";
const room = code => doc(db, ROOMS, code);

const authReady = new Promise((resolve, reject) => {
  onAuthStateChanged(auth, user => { if (user) resolve(user); });
  signInAnonymously(auth).catch(reject);
});

// 공용 비속어 필터 (app-config/profanity-words)
let badWords = null;
const normalize = t => t.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "");
export async function containsProfanity(text){
  if (!badWords) {
    try {
      const snap = await getDoc(doc(db, "app-config", "profanity-words"));
      badWords = snap.exists() ? (snap.data().words || []) : [];
    } catch (e) { badWords = []; }
  }
  return badWords.some(w => normalize(text).includes(normalize(w)));
}

export async function uid(){ return (await authReady).uid; }

// 방 만들기: 비어 있는 네 자리 코드를 골라 방을 연다. 1시간 뒤 지워지도록 expireAt 을 넣는다(Firestore TTL).
export async function create(name){
  const me = await uid();
  for (;;) {
    const code = String(Math.floor(1000 + Math.random() * 9000));
    if ((await getDoc(room(code))).exists()) continue;
    await setDoc(room(code), {host: me, hostName: name, guest: null, guestName: "", status: "waiting",
      first: "host", chain: [], winner: "", reason: "", createdAt: serverTimestamp(),
      expireAt: Timestamp.fromMillis(Date.now() + 3600 * 1000)});
    return code;
  }
}

// 방 들어가기: 기다리는 방이면 손님으로 들어가 바로 시작한다. 실패하면 이유를 글로 돌려준다.
export async function join(code, name){
  const me = await uid();
  return runTransaction(db, async t => {
    const snap = await t.get(room(code));
    const r = snap.data();
    // TTL 삭제는 바로 되지 않으므로, 1시간이 지난 방은 없는 방으로 본다
    if (!r || r.expireAt.toMillis() < Date.now()) return "그런 방이 없어요.";
    if (r.host === me) return "내가 만든 방이에요.";
    if (r.status !== "waiting") return "이미 시작한 방이에요.";
    t.update(room(code), {guest: me, guestName: name, status: "playing"});
    return "";
  });
}

export const watch = (code, fn) => onSnapshot(room(code), snap => fn(snap.exists() ? snap.data() : null));

// 단어 내기: 내 차례이고 그사이 단어가 늘지 않았을 때만 붙인다. 한방 단어면 바로 이긴다.
export async function play(code, me, word, kill){
  return runTransaction(db, async t => {
    const r = (await t.get(room(code))).data();
    const turn = r.chain.length % 2 === 0 ? r.first : (r.first === "host" ? "guest" : "host");
    if (r.status !== "playing" || turn !== me) return false;
    const next = {chain: [...r.chain, word]};
    if (kill) Object.assign(next, {status: "over", winner: me, reason: "kill"});
    t.update(room(code), next);
    return true;
  });
}

// 게임 끝내기 (기권·시간 초과·상대 응답 없음). 이미 끝났으면 그대로 둔다.
export async function end(code, winner, reason){
  return runTransaction(db, async t => {
    const r = (await t.get(room(code))).data();
    if (r.status === "playing") t.update(room(code), {status: "over", winner, reason});
  });
}

// 다시 하기: 먼저 하는 사람을 바꿔 새 판을 시작한다.
export async function rematch(code){
  return runTransaction(db, async t => {
    const r = (await t.get(room(code))).data();
    if (r.status === "over") t.update(room(code), {status: "playing", chain: [], winner: "", reason: "",
      first: r.first === "host" ? "guest" : "host"});
  });
}

export const remove = code => deleteDoc(room(code));
