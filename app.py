title:Guia de Configuração - Chá de Casa Nova:guia_configuracao_notion.html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guia de Configuração - Casinha Sara e Luis</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen pb-12">

    <!-- Header -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-5xl mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <div class="bg-pink-500/10 p-2.5 rounded-xl border border-pink-500/20 text-pink-500">
                    <i class="fa-solid fa-house-chimney text-xl"></i>
                </div>
                <div>
                    <h1 class="text-lg font-bold">Casinha Sara e Luis</h1>
                    <p class="text-xs text-slate-400">Guia Prático para Lista de Presentes no Notion</p>
                </div>
            </div>
            <span class="bg-emerald-500/10 text-emerald-400 text-xs px-3 py-1 rounded-full border border-emerald-500/20 font-semibold flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Solução 100% Gratuita
            </span>
        </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 mt-8">
        
        <!-- Alerta Importante sobre o Notion -->
        <div class="bg-amber-500/15 border border-amber-500/30 rounded-2xl p-5 mb-8 flex gap-4 items-start">
            <div class="text-amber-500 text-xl mt-0.5">
                <i class="fa-solid fa-circle-exclamation"></i>
            </div>
            <div>
                <h4 class="font-bold text-amber-400 mb-1">Como funciona a limitação do Notion?</h4>
                <p class="text-sm text-slate-300 leading-relaxed">
                    Quando você publica uma página do Notion como "Site", os convidados entram apenas como <strong>leitores</strong>. Isso significa que eles não conseguem clicar em botões para mudar o status ou digitar nomes diretamente na sua tela. Para resolver isso sem gastar nada, usamos um truque simples: um botão que leva o convidado para um formulário ou WhatsApp para confirmar o presente.
                </p>
            </div>
        </div>

        <!-- Seções em Abas -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            <!-- Coluna da Esquerda: Passo a Passo de Configuração -->
            <div class="md:col-span-2 space-y-6">
                
                <!-- PASSO 1 -->
                <div class="bg-slate-800/50 border border-slate-700/60 rounded-2xl p-6">
                    <div class="flex items-center gap-3 mb-4">
                        <span class="bg-blue-500 text-white w-7 h-7 rounded-full flex items-center justify-center font-bold text-sm">1</span>
                        <h3 class="font-bold text-lg">Criar Propriedades na Galeria</h3>
                    </div>
                    <p class="text-sm text-slate-400 mb-4">
                        Dentro da sua base de dados (da imagem anterior), abra um card e crie exatamente estas propriedades:
                    </p>
                    
                    <div class="space-y-3">
                        <div class="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl border border-slate-800 text-sm">
                            <span class="font-semibold text-slate-300"><i class="fa-solid fa-tag text-blue-400 mr-2"></i>Nome do Item</span>
                            <span class="text-slate-400">Título principal (Ex: Air Fryer)</span>
                        </div>
                        <div class="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl border border-slate-800 text-sm">
                            <span class="font-semibold text-slate-300"><i class="fa-solid fa-dollar-sign text-emerald-400 mr-2"></i>Preço</span>
                            <span class="text-slate-400">Número (Formatar como BRL R$)</span>
                        </div>
                        <div class="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl border border-slate-800 text-sm">
                            <span class="font-semibold text-slate-300"><i class="fa-solid fa-list-check text-purple-400 mr-2"></i>Status</span>
                            <span class="text-slate-400">Seleção (Disponível, Reservado)</span>
                        </div>
                        <div class="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl border border-slate-800 text-sm">
                            <span class="font-semibold text-slate-300"><i class="fa-solid fa-link text-pink-400 mr-2"></i>Botão Presentear</span>
                            <span class="text-slate-400">URL (Link do seu WhatsApp ou Form)</span>
                        </div>
                    </div>
                </div>

                <!-- PASSO 2 -->
                <div class="bg-slate-800/50 border border-slate-700/60 rounded-2xl p-6">
                    <div class="flex items-center gap-3 mb-4">
                        <span class="bg-blue-500 text-white w-7 h-7 rounded-full flex items-center justify-center font-bold text-sm">2</span>
                        <h3 class="font-bold text-lg">Escolher o Método de Pagamento/Reserva</h3>
                    </div>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <!-- Opção A -->
                        <div class="bg-slate-900/80 p-5 rounded-xl border border-slate-800 hover:border-pink-500/30 transition-all">
                            <span class="bg-pink-500/15 text-pink-400 text-xs px-2.5 py-1 rounded-md font-semibold">Método A (Mais Simples)</span>
                            <h4 class="font-bold mt-3 mb-1 text-slate-200">Redirecionar para o WhatsApp</h4>
                            <p class="text-xs text-slate-400 leading-relaxed">
                                Você cria um link de WhatsApp personalizado (usando geradores como o Convertte) com o texto: 
                                <em>"Oi Sara e Luis, quero dar de presente a Air Fryer!"</em>. 
                                Quando o convidado clica, ele já fala com você, você manda o Pix e depois marca como reservado.
                            </p>
                        </div>
                        <!-- Opção B -->
                        <div class="bg-slate-900/80 p-5 rounded-xl border border-slate-800 hover:border-violet-500/30 transition-all">
                            <span class="bg-violet-500/15 text-violet-400 text-xs px-2.5 py-1 rounded-md font-semibold font-medium">Método B (Profissional)</span>
                            <h4 class="font-bold mt-3 mb-1 text-slate-200">Formulário Gratuito Tally</h4>
                            <p class="text-xs text-slate-400 leading-relaxed">
                                Crie um formulário grátis em <span class="text-violet-400 font-semibold">Tally.so</span>. Lá você coloca o seu QR Code Pix, campo para Nome e opção Anônima. O Tally integra direto com o Notion de graça, alimentando uma planilha de confirmação para você.
                            </p>
                        </div>
                    </div>
                </div>

                <!-- PASSO 3 -->
                <div class="bg-slate-800/50 border border-slate-700/60 rounded-2xl p-6">
                    <div class="flex items-center gap-3 mb-4">
                        <span class="bg-blue-500 text-white w-7 h-7 rounded-full flex items-center justify-center font-bold text-sm">3</span>
                        <h3 class="font-bold text-lg">Como organizar as fotos no Notion</h3>
                    </div>
                    <p class="text-sm text-slate-300 mb-3">
                        Para que a foto do presente apareça direto no quadradinho do seu site:
                    </p>
                    <ol class="list-decimal list-inside text-xs text-slate-400 space-y-2 leading-relaxed">
                        <li>Abra a página do item (como a Air Fryer) e arraste a foto diretamente para o corpo da página.</li>
                        <li>No menu da Galeria (onde aparecem todos os itens), clique no botão de 3 pontinhos (<i class="fa-solid fa-ellipsis"></i>).</li>
                        <li>Vá em <strong>Layout</strong> e mude a propriedade <strong>Visualização do cartão</strong> para <strong>Conteúdo da página</strong>.</li>
                    </ol>
                </div>

            </div>

            <!-- Coluna da Direita: SIMULADOR INTERATIVO -->
            <div class="space-y-6">
                <div class="bg-slate-800 border-2 border-pink-500/30 rounded-3xl p-6 relative overflow-hidden shadow-xl shadow-pink-500/5">
                    
                    <div class="absolute -top-3 -right-3 w-24 h-24 bg-pink-500/10 rounded-full blur-2xl"></div>
                    
                    <h3 class="text-xl font-bold mb-1 flex items-center gap-2">
                        <i class="fa-solid fa-wand-magic-sparkles text-pink-500 text-base"></i>
                        Simulador de Item
                    </h3>
                    <p class="text-xs text-slate-400 mb-6">Teste abaixo como vai funcionar a experiência do convidado e a sua.</p>

                    <!-- Preview do Notion Card -->
                    <div class="bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden" id="notion-card">
                        <div class="h-44 bg-slate-950 relative flex items-center justify-center p-4">
                            <img src="https://images.unsplash.com/photo-1621972750749-0fbb1abb7736?q=80&w=600&auto=format&fit=crop" 
                                 alt="Air Fryer" 
                                 class="h-full object-contain rounded-lg">
                            <span id="card-status-badge" class="absolute top-3 right-3 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                                🔴 Disponível
                            </span>
                        </div>
                        <div class="p-4">
                            <h4 class="font-bold text-base text-slate-100">Air Fryer Digital</h4>
                            <p class="text-xs text-slate-400 mt-1">4L - Cor Preta para combinar com a cozinha</p>
                            
                            <div class="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between">
                                <div>
                                    <span class="text-[10px] text-slate-500 uppercase block tracking-wider font-semibold">Preço Sugerido</span>
                                    <span class="text-base font-bold text-emerald-400">R$ 350,00</span>
                                </div>
                                <button onclick="openGiftModal()" id="btn-gift" class="bg-pink-600 hover:bg-pink-700 text-white text-xs font-bold px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 shadow-lg shadow-pink-600/10">
                                    <i class="fa-solid fa-gift"></i>
                                    Dar de Presente
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- MOCK DO POPUP DE PAGAMENTO (Simulando o link que abre para o convidado) -->
                    <div id="payment-modal" class="hidden mt-6 bg-slate-950 p-5 rounded-2xl border border-pink-500/40 animate-fade-in">
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-bold text-pink-400 uppercase tracking-wider">Passo do Convidado</span>
                            <button onclick="closeGiftModal()" class="text-slate-500 hover:text-slate-300"><i class="fa-solid fa-xmark"></i></button>
                        </div>
                        
                        <div class="text-center py-2">
                            <p class="text-xs text-slate-400 mb-3">Escaneie o QR Code ou use a chave Pix abaixo:</p>
                            
                            <!-- QR Code Fake -->
                            <div class="w-32 h-32 bg-white p-2 rounded-xl mx-auto mb-3 flex items-center justify-center">
                                <i class="fa-solid fa-qrcode text-slate-900 text-8xl"></i>
                            </div>
                            
                            <div class="bg-slate-900 p-2 rounded-lg border border-slate-800 text-[11px] mb-4 font-mono select-all cursor-pointer flex justify-between items-center px-3" onclick="copyPix()">
                                <span class="text-slate-300" id="pix-key">chave-pix-sara-e-luis@exemplo.com</span>
                                <i class="fa-solid fa-copy text-pink-500"></i>
                            </div>

                            <!-- Campos de identificação -->
                            <div class="space-y-3 text-left">
                                <div>
                                    <label class="block text-[10px] text-slate-400 mb-1">Seu Nome:</label>
                                    <input type="text" id="guest-name" placeholder="Ex: Tia Maria" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-100 focus:outline-none focus:border-pink-500">
                                </div>
                                <div class="flex items-center gap-2">
                                    <input type="checkbox" id="is-anonymous" class="rounded bg-slate-900 border-slate-800 text-pink-500 focus:ring-0">
                                    <label for="is-anonymous" class="text-xs text-slate-400">Quero dar de forma anônima</label>
                                </div>
                                
                                <button onclick="submitGift()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-2.5 rounded-xl transition-all">
                                    Confirmar Envio do Pix
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- AREA DO PROPRIETÁRIO (Seu painel secreto para gerenciar o Notion) -->
                    <div id="admin-panel" class="hidden mt-6 bg-slate-950 p-4 rounded-2xl border border-slate-800">
                        <div class="flex items-center gap-2 mb-3 text-amber-500 text-xs font-bold uppercase tracking-wider">
                            <i class="fa-solid fa-user-shield"></i>
                            Painel dos Donos (Sara & Luis)
                        </div>
                        
                        <div class="bg-slate-900 p-3 rounded-xl border border-slate-800 text-xs space-y-2">
                            <p class="text-slate-300">
                                <strong class="text-pink-400">Notificação:</strong> 
                                <span id="notification-text">Aguardando ação...</span>
                            </p>
                            
                            <button onclick="confirmAdminPayment()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded-lg transition-all flex items-center justify-center gap-2 mt-2">
                                <i class="fa-solid fa-check-double"></i>
                                Confirmar Pagamento
                            </button>
                        </div>
                    </div>

                </div>
            </div>

        </div>

    </main>

    <!-- JS de Simulação -->
    <script>
        function openGiftModal() {
            document.getElementById('payment-modal').classList.remove('hidden');
            // Scroll suave até o modal
            document.getElementById('payment-modal').scrollIntoView({ behavior: 'smooth' });
        }

        function closeGiftModal() {
            document.getElementById('payment-modal').classList.add('hidden');
        }

        function copyPix() {
            navigator.clipboard.writeText("chave-pix-sara-e-luis@exemplo.com");
            alert("Chave Pix copiada!");
        }

        function submitGift() {
            const isAnonymous = document.getElementById('is-anonymous').checked;
            const guestName = document.getElementById('guest-name').value;
            
            if (!guestName && !isAnonymous) {
                alert("Por favor, digite seu nome ou selecione a opção de ajuda anônima.");
                return;
            }

            const nameToShow = isAnonymous ? "Alguém Anônimo" : guestName;

            // Fechar modal de pagamento
            document.getElementById('payment-modal').classList.add('hidden');
            
            // Alterar o card para aguardando confirmação
            const badge = document.getElementById('card-status-badge');
            badge.innerText = "🟡 Confirmando Pix";
            badge.className = "absolute top-3 right-3 bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider";

            // Mostrar painel administrativo
            document.getElementById('admin-panel').classList.remove('hidden');
            document.getElementById('notification-text').innerHTML = `<strong>${nameToShow}</strong> enviou o comprovante do presente Air Fryer!`;
        }

        function confirmAdminPayment() {
            // Alterar status final
            const badge = document.getElementById('card-status-badge');
            badge.innerText = "🟢 Reservado";
            badge.className = "absolute top-3 right-3 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider text-slate-900";
            
            // Mudar o botão no card
            const btn = document.getElementById('btn-gift');
            btn.innerHTML = "<i class='fa-solid fa-circle-check'></i> Já fomos ajudados! :)";
            btn.className = "bg-slate-800 text-slate-500 text-xs font-bold px-4 py-2 rounded-xl cursor-not-allowed border border-slate-700";
            btn.disabled = true;

            // Esconder painel de adm
            document.getElementById('admin-panel').classList.add('hidden');
            alert("Sucesso! Item marcado como Reservado no Notion.");
        }
    </script>
</body>
</html>
```eof

O arquivo acima contém todas as instruções organizadas e o simulador interativo da Air Fryer para ajudar na visualização rápida e sem código.

### Resumo do que você fará no Notion:
1. **Adicionar Itens:** Basta seguir a tabela de propriedades sugeridas no guia para colocar fotos, descrições e o valor de cada item.
2. **O Botão "Dar de Presente":** Você colocará um link dentro do Notion que redirecionará o convidado para o seu WhatsApp ou para o formulário gratuito, onde ele pegará sua chave Pix.
3. **Controle de Reservas:** No painel que você configurou no Notion, você simplesmente altera manualmente o status do item de **Disponível** para **Reservado** assim que receber a notificação do convidado.

Dê uma olhada no guia para testar e sinta-se à vontade para me mandar novas dúvidas sobre como personalizar ainda mais essa dinâmica!
