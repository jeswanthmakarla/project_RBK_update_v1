const sell_crops = async (form) => {
    
      let source = '/crops_sell'
      let payload = { 
          method: "POST",
          headers: {
                    'Content-Type': 'application/json'
                    },
          body: JSON.stringify({
                      "rbk_id": rbk_id,
                      "farmer_name": farmer_name,
                      "mandal": farmer_mandal,
                      "survey_no": form['survey_no'].value,
                      "crop_type": form['crop_type'].value,
                      "cut_date": form['cut_date'].value,
                      "qc_date": form['qc_date'].value,
                      "sell_date": form['sell_date'].value,
                      "bags_req": form['bags_req'].value,
                      "vehicle_type_req": form['vehicle_type_req'].value,
                      "pick_up_time": form['pick_up_time'].value,
                      "pick_up_address": form['pick_up_address'].value,
                      "status": "Processing"
                  }) 
          }

      const response = await fetch(source,payload);
      const data = await response.json()
            if (data['status']=='ok'){
              alert(`Crop Details Updated.`)
              window.location.reload()
            }
}
const track_update = async (ele, track_id) => {
    var select_node = ele.previousElementSibling
    
      let source = '/transport_update/track_status'
      let payload = { 
          method: "POST",
          headers: {
                    'Content-Type': 'application/json'
                    },
          body: JSON.stringify({
                      "track_id": track_id,
                      "status": `${select_node.value}`
                  }) 
          }

      const response = await fetch(source,payload);
      const data = await response.json()
            if (data['status']=='ok'){
              alert(`Track ID : ${track_id} Status Uppdated.`)
              window.location.reload()
            }
}

const bags_status = async (id, status, crop_id, track_id) => {
        
    let source = '/mill_update/bags_status'
    let payload = { 
        method: "POST",
        headers: {
                  'Content-Type': 'application/json'
                  },
        body: JSON.stringify({
                    "id": id,
                    "no_of_bags":document.getElementById('d3f4').textContent,
                    "status": status,
                    "crop_id": crop_id,
                    "track_id": track_id
                }) 
        }

    const response = await fetch(source,payload);
    const data = await response.json()
          if (data['status']=='ok'){
            alert(`Bags Status Updated Successfully.`)
            window.location.reload()
          }
  }

  const mill_update = async (form) => {
  
  let source = '/mill_update/mill'
  let payload = { 
      method: "POST",
      headers: {
                'Content-Type': 'application/json'
                },
      body: JSON.stringify({
                  "storage_capacity": form['storage_capacity'].value,
                  "milling_capacity": form['milling_capacity'].value,
                  "dispatched_bags": form['dispatched_bags'].value

              }) 
      }
  const response = await fetch(source,payload);
  const data = await response.json()
        if (data['status']=='ok'){
          alert(`Mill Details Updated Successfully.`)
          window.location.reload()
        }
}