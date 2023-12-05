const { createClient } = require('redis');

async function main() {
  // Crear el cliente de Redis
  const client = createClient();

  // Manejar errores de conexión
  client.on('error', err => console.log('Redis Client Error', err));

  try {
    // Conectar al servidor de Redis
    await client.connect();
    console.log('Conectado a Redis');

    // Realizar operaciones con Redis
    //await client.set('TERMINO', 'False');
    const value = await client.get('TERMINO');
    console.log('LOGO:', value);

    // Resto de las operaciones...

    // Cerrar la conexión cuando hayas terminado
    await client.disconnect();
    console.log('Desconectado de Redis');
  } catch (error) {
    // Manejar errores de manera adecuada
    console.error('Error en las operaciones con Redis:', error);

    // Asegúrate de cerrar la conexión incluso en caso de error
    await client.disconnect();
  }
}

// Llamar a la función principal
main().catch(error => console.error('Error en la función principal:', error));