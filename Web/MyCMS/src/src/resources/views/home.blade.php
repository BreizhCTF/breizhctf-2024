@include('header')
  <!-- Navbar -->
  <nav class="navbar navbar-dark navbar-expand-lg bg-dark">
    <a class="navbar-brand" href="#">MyCMS</a>
    <ul class="navbar-nav mr-auto">
      <li class="nav-item active">
        <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a>
      </li>
      @if(session()->has('email'))
      <li class="nav-item">
        <a class="nav-link" href="/form?id=me">Mes formulaires</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/form">Créer mon formulaire</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/logout">Se déconnecter</a>
      </li>
      @else
      <li class="nav-item">
        <a type="button" class="nav-link" href="#" data-toggle="modal" data-target="#registerModal">S'enregistrer</a>
      </li>
      <li class="nav-item">
        <a type="button" class="nav-link" href="#" data-toggle="modal" data-target="#loginModal">Se connecter</a>
      </li>
      @endif
    </ul>
  </nav>

  @if(session()->has('ok'))
    <div class="alert alert-success">
      {{Session::get('ok')}} 
      {{Session::forget('ok')}}
    </div>
  @endif

  @if(!empty($flag))
    <div class="alert alert-success">
      {{$flag}}
    </div>
  @endif

  <!-- Contenu principal -->
  <div class="container">
    <div class="text-center">
      <h1>MyCMS</h1>
      <p>Bienvenue sur la page principale de MyCMS, le CMS qui permet de créer vos propres formulaire sans écrire une seule ligne de code !</p>
      @if(session()->has('email'))
      <p class="lead"><a href="/createform">Commencez l'aventure !</a></p>
      @else
      <p class="lead"><a href="#" data-toggle="modal" data-target="#loginModal">Commencez l'aventure !</a></p>
      @endif
    </div>
  </div>

<!-- Modal Login -->
<div class="modal fade" id="loginModal" tabindex="-1" aria-labelledby="loginModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="loginModalLabel">Se connecter</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        @if(session()->has('error'))
          @if(session()->get('modal') == 'loginModal')
            <div class="alert alert-danger">
              {{Session::get('error')}} 
            </div>
          @endif
        @endif
        <form method="POST" action="/login">
          @csrf
          <div class="form-group">
            <label for="email">Adresse email</label>
            <input type="email" class="form-control" id="email" name="email" aria-describedby="emailHelp" placeholder="worty@breizhctf.fr">
          </div>
          <div class="form-group">
            <label for="password">Mot de passe</label>
            <input type="password" class="form-control" id="password" name="password" placeholder="**********">
          </div>
          <button type="submit" class="btn btn-primary">Se connecter</button>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Modal Register -->
<div class="modal fade" id="registerModal" tabindex="-1" aria-labelledby="registerModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="registerModalLabel">S'enregistrer</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        @if(session()->has('error'))
          <div class="alert alert-danger">
            {{Session::get('error')}}
          </div>
        @endif
        <form method="POST" action="/register">
          @csrf
          <div class="form-group">
            <label for="email">Adresse email</label>
            <input type="email" class="form-control" id="email" name="email" aria-describedby="emailHelp" placeholder="worty@breizhctf.fr">
          </div>
          <div class="form-group">
            <label for="pseudo">Votre pseudo</label>
            <input type="pseudo" class="form-control" id="pseudo" name="pseudo" aria-describedby="pseudoHelp" placeholder="Worty">
          </div>
          <div class="form-group">
            <label for="password">Mot de passe</label>
            <input type="password" class="form-control" id="password" name="password" placeholder="*********">
          </div>
          <button type="submit" class="btn btn-primary">S'enregistrer</button>
        </form>
      </div>
    </div>
  </div>
</div>
@if(session()->has('error'))
  <script>$('#{{Session::get("modal")}}').modal('show');</script>
  {{Session::forget('modal')}}
  {{Session::forget('error')}}
@endif
@include('footer')