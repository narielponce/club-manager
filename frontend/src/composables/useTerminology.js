import { computed } from 'vue'
import { currentUser } from '../services/user.js'

const dictionaries = {
  club: {
    member: 'Socio',
    members: 'Socios',
    activity: 'Actividad',
    activities: 'Actividades',
    organization: 'Club',
    baseFee: 'Cuota Social',
    professor: 'Profesor',
    professors: 'Profesores',
    debtLabel: 'Cuota'
  },
  academy: {
    member: 'Alumno',
    members: 'Alumnos',
    activity: 'Disciplina',
    activities: 'Disciplinas',
    organization: 'Academia',
    baseFee: 'Inscripción',
    professor: 'Profesor',
    professors: 'Profesores',
    debtLabel: 'Matrícula'
  },
  tutoring: {
    member: 'Estudiante',
    members: 'Estudiantes',
    activity: 'Clase',
    activities: 'Clases',
    organization: 'Emprendimiento',
    baseFee: 'Inscripción',
    professor: 'Tutor',
    professors: 'Tutores',
    debtLabel: 'Cobro'
  }
}

export function useTerminology() {
  const tenantType = computed(() => {
    return currentUser.value?.club?.tenant_type || 'club'
  })

  const t = (key) => {
    const dict = dictionaries[tenantType.value] || dictionaries.club
    return dict[key] || key
  }

  return {
    tenantType,
    t
  }
}
