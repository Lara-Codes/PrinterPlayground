import { api } from './ports'
import { toast } from './toast'

export interface Issue {
    id: number,
    issue: string
}

export function useGetIssues() {
    return {
        async issues() {
            try {
                const response = await api('getissues') // pass rerun job the Job object and desired printer
                if (response.success === true) {
                    return response.issues
                }
            } catch (error) {
                console.error(error)
                toast.error('An error occurred while rerunning the job')
            }
        }
    }
}

export function useCreateIssues() {
    return {
        async createIssue(issue: string) {
            try {
                const response = await api('createissue', { issue })
                if (response) {
                    if (response.success == false) {
                        toast.error(response.message)
                    } else if (response.success === true) {
                        toast.success(response.message)
                    } else {
                        console.error('Unexpected response:', response)
                        toast.error('Failed to create issue. Unexpected response')
                    }
                } else {
                    console.error('Response is undefined or null')
                    toast.error('Failed to create issue. Unexpected response')
                }
            } catch (error) {
                console.error(error)
                toast.error('An error occurred while creating the issue')
            }
        }
    }
}