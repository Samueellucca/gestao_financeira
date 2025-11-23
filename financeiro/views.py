from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Sum
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import RegistroFinanceiro, Categoria
from .forms import RegistroFinanceiroForm, CategoriaForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import json
import csv
import re
from decimal import Decimal

@login_required
def dashboard(request):
    # Pega os filtros de data do GET request
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Começa com todos os registros
    registros = RegistroFinanceiro.objects.all()

    # Aplica os filtros de data se eles existirem
    if data_inicio:
        registros = registros.filter(data__gte=data_inicio)
    if data_fim:
        registros = registros.filter(data__lte=data_fim)

    # Usando agregação do Django para somar os valores no banco de dados
    # O 'or 0' garante que o valor seja 0 se não houver registros.
    total_entradas = registros.filter(categoria__tipo='entrada').aggregate(total=Sum('valor'))['total'] or 0
    total_saidas = registros.filter(categoria__tipo='saida').aggregate(total=Sum('valor'))['total'] or 0

    # O cálculo do saldo permanece o mesmo
    saldo = total_entradas - total_saidas

    # --- Dados para os Gráficos ---
    # Gráfico de Pizza/Doughnut para distribuição de Saídas por Categoria
    saidas_por_categoria = registros.filter(
        categoria__tipo='saida'
    ).values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')

    # Gráfico de Pizza/Doughnut para distribuição de Entradas por Categoria
    entradas_por_categoria = registros.filter(
        categoria__tipo='entrada'
    ).values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')

    context = {
        'request': request, # Passa o request para o contexto para o filtro de data
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo,
        'ultimos_registros': RegistroFinanceiro.objects.select_related('categoria').order_by('-data')[:5],
        
        # Passando os dados do gráfico para o template em formato JSON
        'saidas_chart_labels': json.dumps([item['categoria__nome'] for item in saidas_por_categoria]),
        'saidas_chart_data': json.dumps([float(item['total']) for item in saidas_por_categoria]),
        
        'entradas_chart_labels': json.dumps([item['categoria__nome'] for item in entradas_por_categoria]),
        'entradas_chart_data': json.dumps([float(item['total']) for item in entradas_por_categoria]),
    }
    return render(request, 'financeiro/dashboard.html', context)


class RegistroListView(LoginRequiredMixin, ListView):
    model = RegistroFinanceiro
    template_name = 'financeiro/registro_list.html'
    context_object_name = 'registros'
    paginate_by = 20

    def get_queryset(self):
        queryset = RegistroFinanceiro.objects.select_related('categoria').order_by('-data')
        
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')

        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona os parâmetros de filtro (GET) ao contexto para uso no template
        context['request'] = self.request
        return context

@login_required
def export_registros_csv(request):
    """
    Exporta os registros financeiros para um arquivo CSV, aplicando os filtros de data.
    """
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="registros_financeiros.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8')) # BOM para Excel entender UTF-8

    writer = csv.writer(response, delimiter=';')
    # Escreve o cabeçalho
    writer.writerow(['Data', 'Descrição', 'Categoria', 'Tipo', 'Valor'])

    # Filtra os registros da mesma forma que a ListView
    queryset = RegistroFinanceiro.objects.select_related('categoria').order_by('-data')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if data_inicio:
        queryset = queryset.filter(data__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(data__lte=data_fim)

    # Escreve os dados
    for registro in queryset:
        writer.writerow([
            registro.data.strftime('%d/%m/%Y'),
            registro.descricao,
            registro.categoria.nome,
            registro.categoria.get_tipo_display(),
            str(registro.valor).replace('.', ',') # Formato para Excel em português
        ])

    return response

class RegistroCreateView(LoginRequiredMixin, CreateView):
    model = RegistroFinanceiro
    form_class = RegistroFinanceiroForm
    template_name = 'financeiro/registro_form.html'
    success_url = reverse_lazy('financeiro:registro_list')

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

class RegistroUpdateView(LoginRequiredMixin, UpdateView):
    model = RegistroFinanceiro
    form_class = RegistroFinanceiroForm
    template_name = 'financeiro/registro_form.html'
    success_url = reverse_lazy('financeiro:registro_list')

class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'financeiro/categoria_form.html'
    success_url = reverse_lazy('financeiro:registro_novo')

class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'financeiro/categoria_list.html'
    context_object_name = 'categorias'
    ordering = ['nome']

class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'financeiro/categoria_form.html'
    success_url = reverse_lazy('financeiro:categoria_list')

class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'financeiro/categoria_confirm_delete.html'
    success_url = reverse_lazy('financeiro:categoria_list')

@login_required
def excluir_registro(request, pk):
    registro = get_object_or_404(RegistroFinanceiro, pk=pk)
    registro.delete()
    # Redireciona para a página de onde o usuário veio, ou para o dashboard como fallback
    return redirect(request.META.get('HTTP_REFERER', reverse_lazy('financeiro:dashboard')))

@login_required
def processar_voz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command = data.get('command', '').lower()
            
            # Padrões aprimorados para maior flexibilidade
            # Aceita variações como "gastei 50 com...", "paguei 50 reais em...", "despesa de 50 para..."
            padrao_saida = re.search(r'(gastei|paguei|saída de|despesa de|comprei) ([\d,\.]+) ?(reais|brl)? (?:com|em|no|na|de|para) (.*)', command)
            padrao_entrada = re.search(r'(recebi|ganhei|entrada de|oferta de|dízimo de) ([\d,\.]+) ?(reais|brl)? (?:de|do|da|como|pelo|pela|referente a) (.*)', command)

            valor_str = None
            descricao = None
            tipo = None

            if padrao_saida:
                tipo = 'saida'
                valor_str = padrao_saida.group(2).strip()
                descricao = padrao_saida.group(4).strip()
            elif padrao_entrada:
                tipo = 'entrada'
                valor_str = padrao_entrada.group(2).strip()
                descricao = padrao_entrada.group(4).strip()
            
            if not tipo:
                return JsonResponse({'success': False, 'message': f'Comando não reconhecido. Eu ouvi: "{command}". Tente usar frases como "Gastei 50 com..." ou "Recebi 100 de...".'})

            # Converte o valor para Decimal
            valor = Decimal(valor_str.replace(',', '.'))

            # Lógica para criar ou encontrar a categoria (usando a primeira palavra da descrição)
            # Se a descrição for curta, usa ela toda como categoria.
            palavras_descricao = descricao.split()
            if len(palavras_descricao) <= 2:
                nome_categoria = descricao.capitalize()
            else:
                nome_categoria = palavras_descricao[0].capitalize()

            categoria, criada = Categoria.objects.get_or_create(
                nome=nome_categoria,
                defaults={'tipo': tipo}
            )
            
            if not criada and categoria.tipo != tipo:
                return JsonResponse({'success': False, 'message': f'A categoria "{nome_categoria}" já existe como {categoria.get_tipo_display()}.'})

            # Cria o registro financeiro
            RegistroFinanceiro.objects.create(
                data=timezone.now().date(), # Adiciona a data atual
                descricao=descricao, 
                valor=valor, 
                categoria=categoria, 
                criado_por=request.user
            )

            return JsonResponse({'success': True, 'message': f'Registro de {tipo} de R${valor:.2f} ("{descricao}") criado com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ocorreu um erro: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)
