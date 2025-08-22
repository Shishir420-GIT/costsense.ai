import type { WebSocketMessage, AnalysisRequest } from '@/types/agent.types';

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 1000;
  private listeners: Map<string, ((data: any) => void)[]> = new Map();

  constructor() {
    this.connect();
  }

  private connect() {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const fullUrl = `${wsUrl}/ws/cost-analysis`;
    
    try {
      this.ws = new WebSocket(fullUrl);
      
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connected', { status: 'connected' });
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 WebSocket message:', data);
          this.emit(data.type, data);
          this.emit('message', data);
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };
      
      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason);
        this.emit('disconnected', { code: event.code, reason: event.reason });
        
        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`🔄 Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
          
          setTimeout(() => {
            this.connect();
          }, this.reconnectTimeout * this.reconnectAttempts);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.emit('error', { error });
      };
      
    } catch (error) {
      console.error('❌ WebSocket connection error:', error);
    }
  }

  public send(message: AnalysisRequest) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      console.log('📤 WebSocket sent:', message);
    } else {
      console.error('❌ WebSocket not connected');
      throw new Error('WebSocket not connected');
    }
  }

  public on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  public off(event: string, callback?: (data: any) => void) {
    if (!this.listeners.has(event)) return;
    
    if (callback) {
      const callbacks = this.listeners.get(event)!;
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    } else {
      this.listeners.set(event, []);
    }
  }

  private emit(event: string, data: any) {
    if (this.listeners.has(event)) {
      this.listeners.get(event)!.forEach(callback => callback(data));
    }
  }

  public disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // Convenience methods for specific analysis types
  public requestCostAnalysis(query: string) {
    this.send({
      type: 'cost_analysis',
      query
    });
  }

  public requestOptimization(query: string, service?: string) {
    this.send({
      type: 'optimization_request',
      query,
      service
    });
  }

  public requestParallelAnalysis(query: string) {
    this.send({
      type: 'parallel_analysis',
      query
    });
  }

  public requestComprehensiveAnalysis(query: string) {
    this.send({
      type: 'comprehensive_analysis',
      query
    });
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;