function [] = test3(X)
    Obs = mmread("sparseN.mm.mtx");
    [m,n] = size(Obs);
    obsf = Obs';
    obsf = obsf./5;
    DCG_SIZE = 400;
%     mX = X(23:28);
%     aX = X(29:561);
    %GENRE
%     X = input;
    gX = X(:,1:22);
    XR = full(mmread("XR-genre.mm.mtx"));
    Y = full(mmread("Y-genre.mm.mtx"));
    X = full(mmread("X-genre.mm.mtx"));
    %M = full(mmread("M-genre.mm.mtx"));
    U = full(mmread("U-genre.mm.mtx"));
    V = full(mmread("V-genre.mm.mtx"));
    TX = gX/XR; %QR = N
    [rate, rank, U, V] = online_train(obsf, U, V, X,Y);
    save('onlineUg.mat','U')
    save('onlineVg.mat','V')

    N = X * U * V * Y'; %X * M * Y'
    [~,SNg] = sort(N, 2, 'descend');

%     %MPAA
%     %mX = X(:,23:28);
%     XR = full(mmread("XR-mpaa.mm.mtx"));
%     Y = full(mmread("Y-mpaa.mm.mtx"));
%     X = full(mmread("X-mpaa.mm.mtx"));
%     %M = full(mmread("M-mpaa.mm.mtx"));
%     U = full(mmread("U-mpaa.mm.mtx"));
%     V = full(mmread("V-mpaa.mm.mtx"));
% 
%     %mpaa
%     %TX = mX/XR; %QR = N
%     [rate, rank, U, V] = online_train(obsf, U, V, X, Y);
%     save('onlineUm.mat','U')
%     save('onlineVm.mat','V')
%     N = X * U *V * Y'; %X * M * Y'
%     [~,SNm] = sort(N, 2, 'descend'); %sort for best 

%%
% ONLINE LEARNING
%%


    best_ranks = zeros(5000,1188);
    for i = 1:5000
        agg = vertcat(SNg(i,:));
        best_rank = zeros(1,1188);
        for j=1:1188
            winner = election(agg, 'dictator');
            best_rank(j) = winner;
            agg(agg ==winner) = [];
        end
        best_ranks(i, :) = best_rank;
    end
    
    %w = election(agg, '')
%     r = rank_lp(agg)
    
    vagm = compareNDCG(best_ranks)
%     save('gmResult.mat','vagm')
%     
%     %actor
%     %mX = X(:,23:28);
%     XR = full(mmread("XR-actor.mm.mtx"));
%     Y = full(mmread("Y-actor.mm.mtx"));
%     X = full(mmread("X-actor.mm.mtx"));
%     %M = full(mmread("M-mpaa.mm.mtx"));
%     U = full(mmread("U-actor.mm.mtx"));
%     V = full(mmread("V-actor.mm.mtx"));
% 
%     %mpaa
%     %TX = mX/XR; %QR = N
%     [rate, rank, U, V] = online_train(obsf, U, V, X, Y);
%     save('onlineUa.mat','U')
%     save('onlineVa.mat','V')
%     N = X * U *V * Y'; %X * M * Y'
%     [~,SNa] = sort(N, 2, 'descend'); %sort for best 
% 
% %%
% % ONLINE LEARNING
% %%
% 
% 
%     best_ranks = zeros(5000,1188);
%     for i = 1:5000
%         agg = vertcat(SNa(i,:));
%         best_rank = zeros(1,1188);
%         for j=1:1188
%             winner = election(agg, 'dictator');
%             best_rank(j) = winner;
%             agg(agg ==winner) = [];
%         end
%         best_ranks(i, :) = best_rank;
%     end
%     
%     vaa = compareNDCG(best_ranks)
%     save('aResult.mat','vaa')
%     
%     best_ranks = zeros(5000,1188);
%     for i = 1:5000
%         agg = vertcat(SNg(i,:), SNm(i,:), SNa(i,:));
%         best_rank = zeros(1,1188);
%         for j=1:1188
%             winner = election(agg, 'dictator');
%             best_rank(j) = winner;
%             agg(agg ==winner) = [];
%         end
%         best_ranks(i, :) = best_rank;
%     end
%     
%     vagma = compareNDCG(best_ranks)
%     save('gmaResult.mat','vagma')
% end