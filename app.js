// Obtener referencias a los elementos select
const yearSelect = document.getElementById('year');
const companySelect = document.getElementById('company');
const campaignSelect = document.getElementById('campaign');

// Función para cargar años desde el backend
async function cargarAños() {
  try {
    const dataFromBackend = await obtenerDatosBackend('http://127.0.0.1:3000/api/files');
    const años = obtenerAños(dataFromBackend);
    cargarOpciones(yearSelect, años);

    // Al cargar la página, también cargamos las compañías y campañas iniciales
    await cargarCompañias();
    await cargarCampañas();
    actualizarRuta()
  } catch (error) {
    console.error('Error al cargar los años desde el backend:', error);
  }
}

// Función para cargar compañías desde el backend
async function cargarCompañias() {
  try {
    const añoSeleccionado = yearSelect.value;
    const dataFromBackend = await obtenerDatosBackend('http://127.0.0.1:3000/api/files');
    const compañías = obtenerCompañías(dataFromBackend, añoSeleccionado);
    cargarOpciones(companySelect, compañías);
    // También cargamos las campañas al cambiar el año
    await cargarCampañas();
    actualizarRuta()
  } catch (error) {
    console.error('Error al cargar las compañías desde el backend:', error);
  }
}

// Función para cargar campañas desde el backend
async function cargarCampañas() {
  try {
    const añoSeleccionado = yearSelect.value;
    const compañíaSeleccionada = companySelect.value;
    const dataFromBackend = await obtenerDatosBackend('http://127.0.0.1:3000/api/files');
    const campañas = obtenerCampañas(dataFromBackend, añoSeleccionado, compañíaSeleccionada);
    cargarOpciones(campaignSelect, campañas);

    // También cargamos los videos e imágenes al cambiar la campaña
    await cargarVideos();
    await cargarImagenes();
    actualizarRuta()
  } catch (error) {
    console.error('Error al cargar las campañas desde el backend:', error);
  }
}
// Función para cargar opciones en un select
function cargarOpciones(select, opciones) {
  // Limpiamos las opciones actuales
  select.innerHTML = "";
  // Agregamos las nuevas opciones
  opciones.forEach(opcion => {
    const option = document.createElement("option");
    option.value = opcion;
    option.text = opcion;
    select.add(option);
  });
}

// Función para obtener años únicos de los datos
function obtenerAños(data) {
  return [...new Set(data.map(item => item.name.split("/")[0]))];
}

function obtenerCompañías(data, año) {
  const compañías = data
    .filter(item => item.name.startsWith(`${año}/`))
    .map(item => item.name.split("/")[1])
    .filter(Boolean); // Filtra valores en blanco o nulos
  return [...new Set(compañías)];
}

function obtenerCampañas(data, año, compañía) {
  const campañas = data
    .filter(item => item.name.startsWith(`${año}/${compañía}/`))
    .map(item => item.name.split("/")[3])
    .filter(Boolean); // Filtra valores en blanco o nulos
  return [...new Set(campañas)];
}

// Función para obtener datos desde el backend
async function obtenerDatosBackend(url) {
  try {
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    console.error('Error al obtener datos desde el backend:', error);
    throw error;
  }
}

// Función para cargar videos desde el backend según la campaña
async function cargarVideos() {
  try {
    const añoSeleccionado = yearSelect.value;
    const compañíaSeleccionada = companySelect.value;
    const campañaSeleccionada = campaignSelect.value;
    const dataFromBackend = await obtenerDatosBackend('http://127.0.0.1:3000/api/files');
    const videos = obtenerVideos(dataFromBackend, añoSeleccionado, compañíaSeleccionada, campañaSeleccionada);
    cargarLista('video-list', videos);
  } catch (error) {
    console.error('Error al cargar los videos desde el backend:', error);
  }
}

// Función para cargar imágenes desde el backend
async function cargarImagenes() {
  try {
    const añoSeleccionado = yearSelect.value;
    const compañíaSeleccionada = companySelect.value;
    const campañaSeleccionada = campaignSelect.value;
    const dataFromBackend = await obtenerDatosBackend('http://127.0.0.1:3000/api/files');
    const imagenes = obtenerImagenes(dataFromBackend, añoSeleccionado, compañíaSeleccionada, campañaSeleccionada);
    cargarLista('image-list', imagenes);
  } catch (error) {
    console.error('Error al cargar las imágenes desde el backend:', error);
  }
}

// Función para cargar la lista en el elemento con el id dado
function cargarLista(elementId, lista, videoContainer, imageContainer) {
  const listaElement = document.getElementById(elementId);
  listaElement.innerHTML = "";

  lista.forEach(item => {
    const li = document.createElement("li");
    const link = document.createElement("a");
    link.textContent = item;

    // Agrega un evento de clic para descargar el archivo
    link.addEventListener('click', function(event) {
      event.preventDefault(); // Evita que el navegador siga el enlace
      event.stopPropagation(); // Evita que el evento se propague

      const añoSeleccionado = yearSelect.value;
      const compañíaSeleccionada = companySelect.value;
      const campañaSeleccionada = campaignSelect.value;
      const ruta = `${añoSeleccionado}/${compañíaSeleccionada}/Videos/${campañaSeleccionada}/${item}`;

      // Obtén la URL completa del archivo
      const url = `http://127.0.0.1:3000/api/files/download?path=${ruta}`;

      // Hacer una petición al servidor para manejar la descarga
      fetch(url)
        .then(response => response.blob())
        .then(blob => {
          // Crear un enlace temporal para descargar el archivo
          const downloadLink = document.createElement('a');
          downloadLink.href = window.URL.createObjectURL(blob);
          downloadLink.download = item;

          // Agregar el enlace al documento y simular un clic
          document.body.appendChild(downloadLink);
          downloadLink.click();

          // Limpiar el enlace temporal
          document.body.removeChild(downloadLink);
        })
        .catch(error => {
          console.error('Error al descargar el archivo:', error);
        });
    });

    li.appendChild(link);
    listaElement.appendChild(li);
  });
}





// Función para obtener videos únicos para un año, compañía y campaña dados
function obtenerVideos(data, año, compañía, campaña) {
  const videos = data
    .filter(item => item.name.startsWith(`${año}/${compañía}/Videos/${campaña}/`))
    .map(item => item.name.split("/").pop()) // Obtener el nombre del video
    .filter(name => name.endsWith('.mp4')); // Filtrar solo archivos .mp4
  return [...new Set(videos)];
}

// Función para obtener imágenes únicas para un año, compañía y campaña dados
function obtenerImagenes(data, año, compañía, campaña) {
  const ruta = `${año}/${compañía}/Videos/${campaña}/`;
  const extensionesPermitidas = ['jpg', 'jpeg', 'png'];
  
  const imagenes = data
    .filter(item => item.name.startsWith(ruta))
    .map(item => item.name.replace(`${ruta}`, ''))
    .filter(nombreArchivo => {
      const extension = nombreArchivo.split('.').pop().toLowerCase();
      return extensionesPermitidas.includes(extension);
    })
    .filter(Boolean); // Filtra valores en blanco o nulos
  
  return [...new Set(imagenes)];
}


// Función para agregar video
function agregarVideo(event) {
  const fileInput = event.target;
  const selectedFile = fileInput.files[0];

  // Ahora puedes hacer algo con el archivo seleccionado, como enviarlo al servidor
  subirVideoAlServidor(selectedFile);
}

function subirVideoAlServidor(videoFile) {
  // Obtén la información actualmente seleccionada (puedes ajustar esto según tus necesidades)
  const añoSeleccionado = yearSelect.value;
  const compañíaSeleccionada = companySelect.value;
  const campañaSeleccionada = campaignSelect.value;

  // Construye la ruta deseada
  const ruta = `${añoSeleccionado}/${compañíaSeleccionada}/Videos/${campañaSeleccionada}`;

  // Crea un formulario para enviar al servidor
  const formData = new FormData();
  formData.append('file', videoFile);
  formData.append('ruta', ruta);  // Envía la ruta al servidor
  enviarConfiguracionAlServidor('video')
  fetch('http://127.0.0.1:3000/api/files/upload', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log('Video subido exitosamente:', data.message);
        abrirModal('Video subido con éxito');
        cargarVideos();
      } else {
        console.error('Error al subir el video:', data.message);
      }
    })
    .catch(error => {
      console.error('Error al subir el video:', error);
    });
}

// Función para agregar imagen
function agregarImagen(event) {
  const fileInput = event.target;
  const selectedFile = fileInput.files[0];

  // Ahora puedes hacer algo con el archivo seleccionado, como enviarlo al servidor
  subirImagenAlServidor(selectedFile);
}

// Función para subir imagen al servidor
function subirImagenAlServidor(imagenFile) {
  const añoSeleccionado = yearSelect.value;
  const compañíaSeleccionada = companySelect.value;
  const campañaSeleccionada = campaignSelect.value;
  const ruta = `${añoSeleccionado}/${compañíaSeleccionada}/Videos/${campañaSeleccionada}`;

  const formData = new FormData();
  formData.append('file', imagenFile);
  formData.append('ruta', ruta);
  enviarConfiguracionAlServidor('imagen')
  fetch('http://127.0.0.1:3000/api/files/upload', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log('Imagen subida exitosamente:', data.message);
        abrirModal('Imagen subida con éxito');
        // Después de cargar la imagen, obtén la lista actualizada y actualiza la interfaz
        cargarImagenes();
      } else {
        console.error('Error al subir la imagen:', data.message);
      }
    })
    .catch(error => {
      console.error('Error al subir la imagen:', error);
    });
}

// Función para agregar campaña
async function agregarCampaña() {
  try {
    const añoSeleccionado = yearSelect.value;
    const compañíaSeleccionada = companySelect.value;
    const nuevaCampaña = prompt('Ingrese el nombre de la nueva campaña:');
    
    if (!nuevaCampaña) {
      return; // Si el usuario cancela o no ingresa un nombre, no hacemos nada
    }

    // Creamos la estructura de la nueva carpeta
    const nuevaRuta = `${añoSeleccionado}/${compañíaSeleccionada}/Videos/${nuevaCampaña}/`;

    // Enviamos una solicitud al backend para crear la carpeta
    await fetch(`http://127.0.0.1:3000/api/files/createFolder?folderPath=${nuevaRuta}`, {
      method: 'POST',
    });

    // Volvemos a cargar las campañas para reflejar la nueva carpeta
    await cargarCampañas();
  } catch (error) {
    console.error('Error al agregar la campaña:', error);
  }
}

function actualizarRuta() {
  const añoSeleccionado = yearSelect.value;
  const compañíaSeleccionada = companySelect.value;
  const campañaSeleccionada = campaignSelect.value;

  const rutaDisplay = document.getElementById('ruta-seleccionada');
  rutaDisplay.textContent = `Ruta: ${añoSeleccionado} > ${compañíaSeleccionada} > ${campañaSeleccionada}`;

  // También puedes utilizar esta ruta para cargar los videos e imágenes si es necesario
  cargarVideos();
  cargarImagenes();
}





function enviarConfiguracionAlServidor(elemento) {
  
  let etiquetasCheckbox = document.getElementById('etiquetasCheckbox').checked;
  let logosCheckbox = document.getElementById('logosCheckbox').checked;
  let personasCheckbox = document.getElementById('personasCheckbox').checked;
  let textosCheckbox = document.getElementById('textosCheckbox').checked;
  let audioCheckbox = document.getElementById('audioCheckbox').checked;
  let textospeechCheckbox = document.getElementById('textospeechCheckbox').checked;

  let imagen_etiquetas = document.getElementById('imagen_etiquetasCheckbox').checked
  let imagen_landmark = document.getElementById('imagen_landmarkCheckbox').checked
  let imagen_caras = document.getElementById('imagen_carasCheckbox').checked
  let imagen_textos = document.getElementById('imagen_textosCheckbox').checked
  
  if (elemento=='video'){
    imagen_etiquetas = false
    imagen_landmark = false
    imagen_caras = false
    imagen_textos = false
  }
  if (elemento=='imagen'){
    etiquetasCheckbox = false
    logosCheckbox = false
    personasCheckbox = false
    textosCheckbox = false
    audioCheckbox = false
    textospeechCheckbox = false
  }

  const configuracion = {
    ETIQUETAS: etiquetasCheckbox,
    LOGOS: logosCheckbox,
    PERSONAS: personasCheckbox,
    TEXTOS: textosCheckbox,
    AUDIO: audioCheckbox,
    TEXTOSPEECH: textospeechCheckbox,
    IMAGEN_ETIQUETAS:imagen_etiquetas,
    IMAGEN_LANDMARK:imagen_landmark,
    IMAGEN_CARAS:imagen_caras,
    IMAGEN_TEXTOS:imagen_textos,
  };

  // Enviar configuración al servidor
  fetch('http://127.0.0.1:3000/api/configuracion', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(configuracion),
  })
    .then(response => response.json())
    .then(data => {
      console.log('Respuesta del servidor:', data);
    })
    .catch(error => {
      console.error('Error al enviar configuración al servidor:', error);
    });
}


// Función para abrir el modal con un mensaje
function abrirModal(mensaje) {
  const modal = document.getElementById('myModal');
  const modalMessage = document.getElementById('modal-message');
  const modalClose = document.getElementById('modal-close');

  // Establecer el mensaje
  modalMessage.textContent = mensaje;

  // Mostrar el modal
  modal.style.display = 'block';

  // Agregar el evento de cierre al botón de cierre
  modalClose.onclick = cerrarModal;
}

// Función para cerrar el modal
function cerrarModal() {
  const modal = document.getElementById('myModal');
  modal.style.display = 'none';
}

// Llamamos a cargarAños al cargar la página
cargarAños();