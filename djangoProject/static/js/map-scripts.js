// map-scripts.js

function inicializarMapas() {
    // Suponha que boleias_existente seja uma lista JS contendo os dados das boleias
    boleias_existente.forEach(function(boleia, index) {
      obterCoordenadas(boleia.origem, boleia.destino, index + 1);
    });
  }
  
  function obterCoordenadas(origem, destino, mapaNumero) {
    var geocoder = new google.maps.Geocoder();
  
    // Geocodificação da origem
    geocoder.geocode({ address: origem }, function (results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        var origemLat = results[0].geometry.location.lat();
        var origemLng = results[0].geometry.location.lng();
  
        // Geocodificação do destino
        geocoder.geocode({ address: destino }, function (results, status) {
          if (status === google.maps.GeocoderStatus.OK) {
            var destinoLat = results[0].geometry.location.lat();
            var destinoLng = results[0].geometry.location.lng();
  
            inicializarMapa(origemLat, origemLng, destinoLat, destinoLng, 'map' + mapaNumero);
          }
        });
      }
    });
  }
  
  function inicializarMapa(origemLat, origemLng, destinoLat, destinoLng, mapaId) {
    var mapa = new google.maps.Map(document.getElementById(mapaId), {
      center: { lat: origemLat, lng: origemLng },
      zoom: 10,
    });
  
    // Adicione marcadores ou linhas de rota conforme necessário
    var origemMarker = new google.maps.Marker({ position: { lat: origemLat, lng: origemLng }, map: mapa, title: 'Origem' });
    var destinoMarker = new google.maps.Marker({ position: { lat: destinoLat, lng: destinoLng }, map: mapa, title: 'Destino' });
  }
  