@include('header')
  <!-- Navbar -->
  <nav class="navbar navbar-dark navbar-expand-lg bg-dark">
    <a class="navbar-brand" href="#">MyCMS - ADMIN</a>
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
@if(session()->has('ok'))
  <div class="alert alert-success">
    {{Session::get('ok')}} 
    {{Session::forget('ok')}}
  </div>
@endif
<div class="container">
  <div class="text-center">
    <p>Liste des actions admins: </p>
    <ul>
      <li><a target="_blank" href="/admin/logs/download?file=/templates/errors.log">Télécharger</a> les logs d'erreur</li>
      <li><a target="_blank" href="/admin/logs/download?file=/templates/error_log_template.txt">Télécharger</a> le template d'erreur</li>
      <li><a href="#" data-toggle="modal" data-target="#changeTemplateModal">Changer</a> le template d'erreur</li>
    </ul>
  </div>
</div>

<!-- Modal Change Template -->
<div class="modal fade" id="changeTemplateModal" tabindex="-1" aria-labelledby="changeTemplateModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="changeTemplateModalLabel">Changer le template</h5>
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
        <form method="POST" action="/admin/logs/template">
          @csrf
          <div class="form-group">
            <label for="template">Contenu du template</label>
            <textarea id="template" name="template" rows="4" cols="50"></textarea><br>
          </div>
          <select name="file">
              <option value="error_log_template.txt">error_log_template.txt</option>
              <option value="error_log_template_beta.txt">error_log_template_beta.txt</option>
              <option value="error_log_template_test.txt">error_log_template_test.txt</option>
          </select>
          <hr/>
          <button type="submit" class="btn btn-primary">Envoyer</button>
        </form>
      </div>
    </div>
  </div>
</div>
@if(session()->has('error'))
  <script>$('#changeTemplateModal').modal('show');</script>
  {{Session::forget('error')}}
@endif
@include('footer')