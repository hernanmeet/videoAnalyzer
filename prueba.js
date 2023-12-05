// Importamos la API de Cloud Storage
const { Storage } = require('@google-cloud/storage');

// Obtenemos las credenciales del archivo JSON
const credentials = require('./vertexai-403121-4e2613b93cf2.json');

// Creamos un cliente de Cloud Storage
const storage = new Storage({
  credentials,
});

// Obtenemos el nombre del bucket
const bucketName = 'videos_online';

// Definimos una función asíncrona para utilizar await
async function listFiles() {
  // Obtenemos la lista de archivos del bucket
  const [files] = await storage.bucket(bucketName).getFiles();

  // Imprimimos solo el nombre de cada archivo
  files.forEach(file => {
    console.log(file.name);
  });
}

// Llamamos a la función asíncrona
listFiles();