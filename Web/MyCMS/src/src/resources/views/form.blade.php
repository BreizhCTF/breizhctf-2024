@include('header')
  <!-- Navbar -->
  <nav class="navbar navbar-dark navbar-expand-lg bg-dark">
    <a class="navbar-brand" href="#">MyCMS</a>
    <ul class="navbar-nav mr-auto">
      <li class="nav-item">
        <a class="nav-link" href="#">Home</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/form?id=me">Mes formulaires</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/form">Créer mon formulaire</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/logout">Se déconnecter</a>
      </li>
    </ul>
  </nav>

@if(empty($error))
  @if(empty($me))
  {!! $html !!}
  @else
    <div class="container">
      <div class="text-center">
        <p>Liste de vos formulaires</p>
        <table class="table table-dark">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">Nom du formulaire</th>
              <th scope="col">Voir</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
          @for ($i = 0; $i < sizeof($names); $i++)
            <tr>
              <th scope="row">{{ $i+1 }}</th>
              <td>{{ $names[$i] }}</td>
              <td><button class="btn btn-primary" onclick="redirectToForm('{{ $names[$i] }}')">Voir le formulaire</button></td>
              <td>
                <button class="btn btn-warning" onclick="exportForm('{{ $names[$i] }}')">Exporter le formulaire</button>
                <button class="btn btn-danger" onclick="deleteForm('{{ $names[$i] }}')">Supprimer le formulaire</button>
              </td>
            </tr>
          @endfor
          </tbody>
        </table>
      </div>
    </div>
    <input type="hidden" id="csrfToken" value="{{ csrf_token() }}"/>
    <script>
      function redirectToForm(name)
      {
        window.location.href="/form?id="+name;
      }

      function exportForm(name)
      {
        window.location.href="/export?name="+name;
      }

      function deleteForm(name)
      {
        $.ajax({
          type: "DELETE",
          url: "/form",
          data: JSON.stringify({"name":name, "_token": $("#csrfToken").val()}),
          contentType: 'application/json; charset=utf-8',
          dataType: 'json',
          success: function(resp)
          {
            if(resp["ok"] !== undefined)
            {
              alert(resp["ok"]);
              window.location.reload();
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
    </script>
  @endif
@else
      <!-- Contenu principal -->
  <div class="container">
    <div class="text-center">
      <h1>Une erreur est survenue... 😞</h1>
      <p class="lead">{{ $error }}</p>
    </div>
  </div>
@endif
@include('footer')