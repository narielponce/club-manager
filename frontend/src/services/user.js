import { ref } from 'vue'

//export const currentUser = ref(null)
const data = await apiFetch('/users/me');
console.log("DATOS RECIBIDOS DEL SERVIDOR:", data); // Esto es lo que queremos ver
currentUser.value = data;
