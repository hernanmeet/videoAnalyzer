const express = require('express');
const cors = require('cors');
const multer = require('multer');
const { Storage } = require('@google-cloud/storage');
const { createClient } = require('redis');
const bodyParser = require('body-parser');

const app = express();


// Obtenemos las credenciales del archivo JSON
const credentials = require('./vertexai-403121-4e2613b93cf2.json');

// Creamos un cliente de Cloud Storage
const storage = new Storage({
  credentials,
});

// Configuración de Multer para manejar la carga de archivos
const upload = multer({ storage: multer.memoryStorage() });

// Habilitar CORS
app.use(cors());

// Ruta de la API para obtener la lista de archivos
app.get('/api/files', async (req, res) => {
  try {
    const [files] = await storage.bucket('videos_online').getFiles();

    // Envia la lista de archivos como respuesta
    res.json(files.map(file => ({ name: file.name })));
  } catch (error) {
    console.error('Error al obtener la lista de archivos:', error);
    res.status(500).send('Error interno del servidor');
  }
});

app.get('/api/files/download', (req, res) => {
  try {
    const filePath = req.query.path;

    // Configura el encabezado para la descarga o visualización según el tipo de contenido
    const contentType = getContentType(filePath);

    if (contentType) {
      res.setHeader('Content-Type', contentType);
    }

    res.setHeader('Content-Disposition', `attachment; filename="${filePath.split('/').pop()}"`);

    // Stream del archivo desde Cloud Storage
    const file = storage.bucket('videos_online').file(filePath);
    const readStream = file.createReadStream();

    // Manejar errores
    readStream.on('error', (err) => {
      console.error('Error al leer el archivo:', err);
      res.status(404).send('No se encontró el archivo');
    });

    readStream.pipe(res);
  } catch (error) {
    console.error('Error al descargar el archivo:', error);
    res.status(500).send('Error interno del servidor');
  }
});


function getContentType(filePath) {
  const extension = filePath.split('.').pop().toLowerCase();

  switch (extension) {
    case 'mp4':
      return 'video/mp4';
    case 'jpg':
    case 'jpeg':
      return 'image/jpeg';
    case 'png':
      return 'image/png';
    // Agrega más tipos de contenido según sea necesario
    default:
      return 'application/octet-stream'; // Tipo de contenido por defecto
  }
}

app.post('/api/files/upload', upload.single('file'), async (req, res) => {
  const client = createClient();

  try {
    const fileBuffer = req.file.buffer;
    const fileName = req.file.originalname;
    const ruta = req.body.ruta || '';
    const filePath = ruta ? `${ruta}/${fileName}` : fileName;

    const file = storage.bucket('videos_online').file(filePath);
    await file.save(fileBuffer);

    console.log(`Archivo subido correctamente: ${filePath}`);

    // Notificar a Redis que la operación ha terminado y actualizar las llaves
    await notifyOperationCompletion(client, filePath);

    res.status(200).json({ success: true, message: 'Archivo subido exitosamente' });
  } catch (error) {
    console.error('Error al cargar el archivo:', error);
    res.status(500).json({ success: false, message: 'Error interno del servidor' });
  } finally {
    // Asegurarse de cerrar la conexión de Redis después de usarla
    await client.quit();
  }
});

async function notifyOperationCompletion(client, filePath) {
  // Conectar al servidor de Redis
  await client.connect();
  
  // Establecer la clave "TERMINO" con el valor "True"
  await client.set('TERMINO', 'True');
  
  // Establecer la clave "PATH_GOOGLE" con el valor del path del archivo
  await client.set('PATH_GOOGLE', "gs://videos_online/"+filePath);

  // Resto de las operaciones con Redis...
}

// Ruta para crear una carpeta
app.post('/api/files/createFolder', async (req, res) => {
  try {
    const folderPath = req.query.folderPath;

    // Crea la carpeta en el bucket
    await storage.bucket('videos_online').file(folderPath).save('');

    res.status(200).send('Carpeta creada exitosamente');
  } catch (error) {
    console.error('Error al crear la carpeta:', error);
    res.status(500).send('Error interno del servidor');
  }
});



// Función para inicializar las llaves en Redis
async function initializeKeys() {
  const client = createClient();

  try {
    // Conectar al servidor de Redis
    await client.connect();
    // Verificar y establecer la llave 'TERMINO'
    const terminoExists = await client.exists('TERMINO');
    if (!terminoExists) {
      await client.set('TERMINO', 'False');
    }

    // Verificar y establecer la llave 'ETIQUETAS'
    const etiquetasExists = await client.exists('ETIQUETAS');
    if (!etiquetasExists) {
      await client.set('ETIQUETAS', 'False');
    }

    // Verificar y establecer la llave 'LOGOS'
    const logosExists = await client.exists('LOGOS');
    if (!logosExists) {
      await client.set('LOGOS', 'False');
    }

    // Verificar y establecer la llave 'PERSONAS'
    const personasExists = await client.exists('PERSONAS');
    if (!personasExists) {
      await client.set('PERSONAS', 'False');
    }

    // Verificar y establecer la llave 'TEXTOS'
    const textosExists = await client.exists('TEXTOS');
    if (!textosExists) {
      await client.set('TEXTOS', 'False');
    }

    // Verificar y establecer la llave 'AUDIO'
    const audioExists = await client.exists('AUDIO');
    if (!audioExists) {
      await client.set('AUDIO', 'False');
    }

    // Verificar y establecer la llave 'TEXTOSPEECH'
    const textospeechExists = await client.exists('TEXTOSPEECH');
    if (!textospeechExists) {
      await client.set('TEXTOSPEECH', 'False');
    }

    // Nuevas claves para checkboxes de imágenes
    const imagenEtiquetasExists = await client.exists('IMAGEN_ETIQUETAS');
    if (!imagenEtiquetasExists) {
      await client.set('IMAGEN_ETIQUETAS', 'False');
    }

    const imagenLandmarkExists = await client.exists('IMAGEN_LANDMARK');
    if (!imagenLandmarkExists) {
      await client.set('IMAGEN_LANDMARK', 'False');
    }

    const imagenCarasExists = await client.exists('IMAGEN_CARAS');
    if (!imagenCarasExists) {
      await client.set('IMAGEN_CARAS', 'False');
    }

    const imagenTextosExists = await client.exists('IMAGEN_TEXTOS');
    if (!imagenTextosExists) {
      await client.set('IMAGEN_TEXTOS', 'False');
    }

  } catch (error) {
    console.error('Error al inicializar las llaves en Redis:', error);
  } finally {
    // Asegurarse de cerrar la conexión de Redis después de usarla
    await client.quit();
  }
}


app.use(bodyParser.json());

//Recibe el parametro de los checkbox
app.post('/api/configuracion', async (req, res) => {
  const client = createClient();
  try {
    // Conectar al servidor de Redis
    await client.connect();
    const configuracion = req.body;

    // Almacenar el estado de los checkboxes en Redis
    Object.keys(configuracion).forEach(key => {
      const value = configuracion[key];
      client.set(key, value.toString().toLowerCase());
    });

    console.log('Configuración recibida y almacenada en Redis:', configuracion);

    // Enviar una respuesta al cliente
    res.json({ success: true, message: 'Configuración recibida y almacenada correctamente' });
  } catch (error) {
    console.error('Error al recibir la configuración de los checkbox:', error);
  } finally {
    // Asegurarse de cerrar la conexión de Redis después de usarla
    await client.quit();
  }
});

// Servir archivos estáticos (como tu index.html y app.js)
app.use(express.static('public'));

// Inicia el servidor en el puerto 3000
const PORT = process.env.PORT || 3000;
async function startServer() {
  try {
    await initializeKeys();
    console.log(`Servidor escuchando en http://localhost:${PORT}`);
  } catch (error) {
    console.error('Error al iniciar el servidor:', error);
  }
}

app.listen(PORT, startServer);
