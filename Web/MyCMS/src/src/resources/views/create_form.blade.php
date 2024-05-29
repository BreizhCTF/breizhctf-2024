@include('header')
  <!-- Navbar -->
  <nav class="navbar navbar-dark navbar-expand-lg bg-dark">
    <a class="navbar-brand" href="#">MyCMS</a>
    <ul class="navbar-nav mr-auto">
      <li class="nav-item active">
        <a class="nav-link" href="#">Home</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/form?id=me">Mes formulaires</a>
      </li>
      <li class="nav-item active">
        <a class="nav-link" href="#">Créer mon formulaire <span class="sr-only">(current)</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/logout">Se déconnecter</a>
      </li>
    </ul>
  </nav>

  <h2 class="text-center">Création de mon formulaire</h2>
  <div class="container text-center">
    <div class="row-4">
        <div id="1" class="form-row align-items-center">
            <div class="col-sm-4 my-1">
            <label for="fieldName1">Nom du champ :</label>
            <input type="text" class="form-control" id="fieldName1" name="fieldName1" placeholder="Nom du champ">
            </div>
            <div class="col-sm-3 my-1">
            <label for="fieldType1">Type de champ :</label>
            <select class="form-control" id="fieldType1" name="fieldType1">
                <option value="email">Email</option>
                <option value="password">Password</option>
                <option value="text">Text</option>
            </select>
            </div>
            <div class="col-sm-3 my-1">
            <label for="fieldSize1">Taille :</label>
            <input type="number" class="form-control" id="fieldSize1" name="fieldSize1" min="5" max="50" placeholder="Taille">
            </div>
        </div>
    </div>
  </div>
  <script src="{{secure_asset('js/script.js')}}"></script>
  <div class="container mt-3">
    <div class="text-center">
      <button type="button" class="btn btn-primary" id="addFieldBtn">Ajouter un champ</button>
      <button type="button" class="btn btn-success" id="createFormBtn" onclick="submitForm()">Créer mon formulaire</button>
    </div>
  </div>
  <input type="hidden" id="csrfToken" value="{{ csrf_token() }}"/>
@include('footer')