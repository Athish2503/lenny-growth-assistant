import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { sessionApi } from '@/api/sessionApi';
import { useSessionStore } from '@/store/sessionStore';
import { useChatStore } from '@/store/chatStore';
import type { Session } from '@/types';

export function useSessions() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { setSessions, addSession, updateSession, removeSession, setActiveSessionId } = useSessionStore();
  const { clearMessages } = useChatStore();

  const query = useQuery({
    queryKey: ['sessions'],
    queryFn: async () => {
      const sessions = await sessionApi.list();
      setSessions(sessions);
      return sessions;
    },
    staleTime: 30000,
  });

  const createMutation = useMutation({
    mutationFn: sessionApi.create,
    onSuccess: (session: Session) => {
      addSession(session);
      setActiveSessionId(session.id);
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      navigate(`/chat/${session.id}`);
    },
  });

  const renameMutation = useMutation({
    mutationFn: ({ id, title }: { id: string; title: string }) =>
      sessionApi.update(id, { title }),
    onSuccess: (session: Session) => {
      updateSession(session.id, session);
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: sessionApi.delete,
    onSuccess: (_: void, id: string) => {
      removeSession(id);
      clearMessages(id);
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      navigate('/chat');
    },
  });

  return {
    sessions: query.data || [],
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    createSession: (input?: Parameters<typeof createMutation.mutate>[0]) =>
      createMutation.mutate(input ?? {}),
    isCreating: createMutation.isPending,
    renameSession: renameMutation.mutate,
    isRenaming: renameMutation.isPending,
    deleteSession: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
  };
}
