export interface Credentials {
  clientId: string
  apiKey: string
}

export function loadCredentials(): Credentials { return { clientId: '', apiKey: '' } }
export function saveCredentials(_: Credentials): void {}
export function clearCredentials(): void {}
export function hasCredentials(_: Credentials): boolean { return false }
