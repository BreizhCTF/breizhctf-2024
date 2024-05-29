var nb_fields = 1;
$(document).ready(function() {
  $('#addFieldBtn').click(function() {
    nb_fields += 1;

    const newField = `
    <div id="${nb_fields}">
      <div class="form-row mt-3 ">
        <div class="col-sm-4 my-1">
          <label for="fieldName${nb_fields}">Nom du champ :</label>
          <input type="text" class="form-control" id="fieldName${nb_fields}" placeholder="Nom du champ">
        </div>
        <div class="col-sm-3 my-1">
          <label for="fieldType${nb_fields}">Type de champ :</label>
          <select class="form-control" id="fieldType${nb_fields}">
            <option value="email">Email</option>
            <option value="password">Password</option>
            <option value="text">Text</option>
          </select>
        </div>
        <div class="col-sm-3 my-1">
          <label for="fieldSize${nb_fields}">Taille :</label>
          <input type="number" class="form-control" id="fieldSize${nb_fields}" min="5" max="50" placeholder="Taille">
        </div>
      </div>
    </div>
    `;

    $(`#${nb_fields-1}`).after(newField);
  });
});


function submitForm()
{
  let data = [];
  for(var i=1; i<=nb_fields; i++)
  {
    data.push({"name": $(`#fieldName${i}`).val() || "", "type": $(`#fieldType${i}`).val() || "", "size": $(`#fieldSize${i}`).val() || 0})
  }
  var name = prompt("Quel est le nom de votre formulaire ?");
  while(name.length <= 0)
  {
    name = prompt("Quel est le nom de votre formulaire ?");
  }
  let to_send = {"name": name, "nb_fields": nb_fields, "content": btoa(JSON.stringify(data)), "_token": $("#csrfToken").val()};
  $.ajax({
    type: "POST",
    url: "/form",
    data: JSON.stringify(to_send),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    success: function(resp)
    {
      if(resp["ok"] !== undefined)
      {
        alert(resp["ok"]);
        window.location.href="/form?id=me";
      }
      else if(resp["error"] !== undefined)
      {
        alert(resp["error"])
      }
      else
      {
        alert("Une erreur est survenue, veuillez réessayer.")
      }
    },
    error: function(resp)
    {
      console.log(resp);
    }
  })
}